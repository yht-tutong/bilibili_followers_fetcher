import asyncio
import aiohttp
import json
import html
import re
from typing import List, Dict, Any
from datetime import datetime


class BilibiliFetcher:
    def __init__(self):
        self.headers = {
            "Origin": "https://www.bilibili.com",
            "Referer": "https://www.bilibili.com/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }
        self.session = None
        self.uid = None
        self.uname = None
        self.output_time = None

    def load_config(self, config_file: str = "config.json") -> bool:
        """从配置文件加载SESSDATA"""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "sessdata" in config and config["sessdata"]:
                    self.headers["Cookie"] = f"SESSDATA={config['sessdata']}"
                    return True
                else:
                    print("配置文件中未找到有效的SESSDATA")
                    return False
        except FileNotFoundError:
            print(f"配置文件 {config_file} 不存在")
            return False
        except json.JSONDecodeError:
            print(f"配置文件 {config_file} 格式错误")
            return False

    def encode_html(self, text: str) -> str:
        """HTML编码函数，与JavaScript版本保持一致"""
        if not isinstance(text, str):
            return ""

        # 基本HTML实体编码
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")

        # 处理空格：连续空格、行首行尾空格转换为&nbsp;
        text = re.sub(r" (?= )|(?<= ) |^ | $", "&nbsp;", text, flags=re.MULTILINE)

        # 换行符转换为<br />
        text = re.sub(r"\r\n|\r|\n", "<br />", text)

        return text

    def format_time(self, timestamp: int) -> str:
        """将Unix时间戳格式化为可读时间"""
        if not timestamp:
            return "未知"
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return "未知"

    async def create_session(self):
        """创建aiohttp会话"""
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        """关闭aiohttp会话"""
        if self.session:
            await self.session.close()

    async def get_user_info(self) -> int:
        """获取自己的UID和用户名"""
        try:
            async with self.session.get(
                "https://api.bilibili.com/x/web-interface/nav"
            ) as response:
                ujson = await response.json()

            if ujson["code"] != 0:
                print(f'获取用户信息失败: {ujson["message"]}')
                raise Exception(f'获取用户信息失败: {ujson["message"]}')

            self.uid = ujson["data"]["mid"]
            self.uname = ujson["data"]["uname"]
            return self.uid

        except Exception as e:
            print(f"获取用户信息时出错: {str(e)}")
            raise

    async def get_followers_page(self, page: int) -> List[Dict[str, Any]]:
        """获取指定页的粉丝信息"""
        try:
            url = f"https://api.bilibili.com/x/relation/fans?vmid={self.uid}&ps=50&pn={page}"
            async with self.session.get(url) as response:
                data = await response.json()

            if data["code"] == 0 and data.get("data") and data["data"].get("list"):
                return data["data"]["list"]
            else:
                print(f'获取第{page}页粉丝信息失败: {data.get("message", "未知错误")}')
                return []

        except Exception as e:
            print(f"请求第{page}页时出错: {str(e)}")
            return []

    async def get_all_followers(self, max_pages: int = 20) -> List[Dict[str, Any]]:
        """获取所有粉丝信息"""
        followers = []

        # 获取前20页粉丝的信息，每页50个
        for i in range(1, max_pages + 1):
            page_followers = await self.get_followers_page(i)
            if not page_followers:
                break
            followers.extend(page_followers)

        return followers

    async def get_followers_detail_info(self, followers: List[Dict[str, Any]]) -> None:
        """获取所有粉丝的详细信息"""
        if not followers:
            return

        uids = [str(f["mid"]) for f in followers]
        uid_str = ",".join(uids)

        try:
            url = f"https://api.vc.bilibili.com/x/im/user_infos?uids={uid_str}"
            async with self.session.get(url) as response:
                cjson = await response.json()

            if cjson["code"] == 0 and cjson.get("data"):
                # 将详细信息合并到粉丝对象中
                for info in cjson["data"]:
                    follower = next(
                        (f for f in followers if f["mid"] == info["mid"]), None
                    )
                    if follower:
                        follower.update(info)

        except Exception as e:
            print(f"获取粉丝详细信息时出错: {str(e)}")

    async def get_followers_stats(self, followers: List[Dict[str, Any]]) -> None:
        """获取所有粉丝的粉丝数统计"""
        if not followers:
            return

        # 分批处理，每批最多20个
        followers_without_stat = [f["mid"] for f in followers]

        while followers_without_stat:
            batch = followers_without_stat[:20]
            followers_without_stat = followers_without_stat[20:]

            try:
                mids_str = ",".join(map(str, batch))
                url = f"https://api.bilibili.com/x/relation/stats?mids={mids_str}"
                async with self.session.get(url) as response:
                    sjson = await response.json()

                if sjson["code"] == 0 and sjson.get("data"):
                    # 将统计信息合并到粉丝对象中
                    for mid_str, stat in sjson["data"].items():
                        mid = int(mid_str)
                        follower = next((f for f in followers if f["mid"] == mid), None)
                        if follower:
                            follower.update(stat)

            except Exception as e:
                print(f"获取粉丝统计信息时出错: {str(e)}")

    def filter_followers(
        self,
        followers: List[Dict[str, Any]],
        filter_default_avatar: bool = True,
        filter_bili_prefix: bool = True,
    ) -> List[Dict[str, Any]]:
        """过滤粉丝列表"""
        if not filter_default_avatar and not filter_bili_prefix:
            print(f"粉丝数量: {len(followers)}")
            return followers

        original_count = len(followers)
        filtered = followers

        # 过滤默认头像
        if filter_default_avatar:
            filtered = [
                f for f in filtered if "/member/noface.jpg" not in f.get("face", "")
            ]
            avatar_filtered = original_count - len(filtered)
            if avatar_filtered > 0:
                print(f"已过滤掉 {avatar_filtered} 个默认头像用户")

        # 过滤 bili_ 开头的用户名
        if filter_bili_prefix:
            before_bili_filter = len(filtered)
            filtered = [
                f
                for f in filtered
                if not (f.get("name") or f.get("uname", "")).startswith("bili_")
            ]
            bili_filtered = before_bili_filter - len(filtered)
            if bili_filtered > 0:
                print(f"已过滤掉 {bili_filtered} 个 bili_ 开头用户")

        print(f"原始粉丝数量: {original_count}")
        print(f"过滤后粉丝数量: {len(filtered)}")

        return filtered

    def generate_json(
        self,
        followers: List[Dict[str, Any]],
        output_file: str = "bilibili_followers.json",
        total_count: int = 0,
    ) -> None:
        """生成JSON文件"""
        self.output_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 简化数据，只保留重要字段
        simplified = []
        for f in followers:
            simplified.append(
                {
                    "mid": f.get("mid"),
                    "name": f.get("name") or f.get("uname"),
                    "face": f.get("face"),
                    "mtime": f.get("mtime"),
                    "mtime_str": self.format_time(f.get("mtime", 0)),
                    "follower": f.get("follower", 0) or f.get("follower_count", 0) or 0,
                }
            )

        output = {
            "owner": {
                "uid": self.uid,
                "name": self.uname,
            },
            "output_time": self.output_time,
            "total_followers": total_count,
            "filtered_followers": len(followers),
            "followers": simplified,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"成功生成粉丝列表JSON文件，共包含 {len(followers)} 个粉丝")

    def generate_html(
        self,
        followers: List[Dict[str, Any]],
        output_file: str = "bilibili_followers.html",
        filter_default_avatar: bool = True,
        filter_bili_prefix: bool = True,
        sort_by_time: bool = True,
        total_count: int = 0,
    ) -> None:
        """生成HTML文件"""
        self.output_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 按关注时间排序（最新的在前）
        if sort_by_time:
            followers = sorted(
                followers, key=lambda x: x.get("mtime", 0) or 0, reverse=True
            )

        # 生成过滤说明
        filter_desc = []
        if filter_default_avatar:
            filter_desc.append("已过滤默认头像")
        if filter_bili_prefix:
            filter_desc.append("已过滤 bili_ 开头用户")
        filter_text = "、".join(filter_desc) if filter_desc else "未过滤"

        # 生成粉丝列表HTML
        followers_html = ""
        for i, f in enumerate(followers, 1):
            name = self.encode_html(f.get("name") or f.get("uname", ""))
            face = f.get("face", "")
            mtime = self.format_time(f.get("mtime", 0))
            follower_count = f.get("follower", 0) or f.get("follower_count", 0) or 0
            mid = f.get("mid", "")

            followers_html += f"""      <tr>
        <td>{i}</td>
        <td><img class="face" src="{face}" referrerpolicy="no-referrer" /></td>
        <td><a href="https://space.bilibili.com/{mid}" target="_blank">{name}</a></td>
        <td>{mid}</td>
        <td>{mtime}</td>
        <td>{follower_count:,}</td>
      </tr>
"""

        owner_info = f'{self.encode_html(self.uname)} (UID: {self.uid})' if self.uname else f'UID: {self.uid}'

        content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>粉丝列表 - {self.encode_html(self.uname)}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>粉丝列表</h1>
      <div class="meta">
        <p><span class="label">Cookie 所有者：</span>{owner_info}</p>
        <p><span class="label">输出时间：</span>{self.output_time}</p>
        <p><span class="label">总粉丝数：</span>{total_count}</p>
        <p><span class="label">过滤后显示：</span>{len(followers)} 位粉丝（{filter_text}）</p>
      </div>
    </div>

    <div class="followers-content">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>头像</th>
            <th>用户名</th>
            <th>UID</th>
            <th>关注时间</th>
            <th>粉丝数</th>
          </tr>
        </thead>
        <tbody>
{followers_html}        </tbody>
      </table>
    </div>
  </div>
</body>
</html>"""

        # 写入文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"成功生成粉丝列表HTML文件，共包含 {len(followers)} 个粉丝")


async def main(
    export_format: str = "both",
    filter_default_avatar: bool = True,
    filter_bili_prefix: bool = True,
    sort_by_time: bool = True,
):
    """主函数"""
    fetcher = BilibiliFetcher()

    try:
        # 加载配置
        if not fetcher.load_config():
            print("请先在 config.json 中配置您的B站Cookie")
            return 1

        # 创建会话
        await fetcher.create_session()

        # 获取用户UID
        await fetcher.get_user_info()

        # 获取所有粉丝信息
        followers = await fetcher.get_all_followers(max_pages=20)

        # 获取所有粉丝的详细信息
        await fetcher.get_followers_detail_info(followers)

        # 获取所有粉丝的粉丝数
        await fetcher.get_followers_stats(followers)

        # 过滤粉丝
        filtered_followers = fetcher.filter_followers(
            followers, filter_default_avatar, filter_bili_prefix
        )

        total_count = len(followers)

        # 根据选择导出文件
        if export_format in ("json", "both"):
            fetcher.generate_json(filtered_followers, "bilibili_followers.json", total_count)

        if export_format in ("html", "both"):
            fetcher.generate_html(
                filtered_followers,
                "bilibili_followers.html",
                filter_default_avatar,
                filter_bili_prefix,
                sort_by_time,
                total_count=total_count,
            )

    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        return 1

    finally:
        # 关闭会话
        await fetcher.close_session()

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="获取B站粉丝列表")
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "html", "both"],
        default="both",
        help="导出格式: json、html 或 both (默认: both)",
    )
    parser.add_argument(
        "--filter",
        choices=["none", "avatar", "bili", "both"],
        default="both",
        help="过滤选项: none(不过滤)、avatar(仅过滤默认头像)、bili(仅过滤bili_开头)、both(都过滤，默认)",
    )
    parser.add_argument(
        "--no-sort",
        action="store_true",
        help="不按关注时间排序（默认按关注时间从新到旧排序）",
    )
    args = parser.parse_args()

    # 解析过滤选项
    filter_default_avatar = args.filter in ("avatar", "both")
    filter_bili_prefix = args.filter in ("bili", "both")

    try:
        exit_code = asyncio.run(
            main(
                export_format=args.format,
                filter_default_avatar=filter_default_avatar,
                filter_bili_prefix=filter_bili_prefix,
                sort_by_time=not args.no_sort,
            )
        )
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        exit(1)
    except Exception as error:
        print(f"程序运行出错: {str(error)}")
        exit(1)
