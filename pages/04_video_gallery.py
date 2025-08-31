#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright notice and include this permission notice.
#
#  For commercial use, including but not limited to selling, distributing, or using the Software as part of any commercial product or service, you must obtain explicit authorization from the author.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Author: 程序那些事
#  email: flydean@163.com
#  Website: [www.flydean.com](http://www.flydean.com)
#  GitHub: [https://github.com/ddean2009/MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus)
#
#  All rights reserved.
#

import streamlit as st

from pages.common import common_ui
from tools.tr_utils import tr
from tools.video_utils import get_video_files_info, format_file_size


common_ui()

st.markdown("<h2 style='text-align: center;padding-top: 0rem;'>AI 视频库</h2>", unsafe_allow_html=True)

toolbar = st.container(border=True)
with toolbar:
    left, right = st.columns([3, 1])
    with left:
        st.caption(tr("展示 final/ 目录中的所有AI生成视频"))
    with right:
        if st.button("🔄 " + tr("刷新"), use_container_width=True):
            st.cache_data.clear()
            st.rerun()


videos = get_video_files_info()

if not videos:
    st.info("📭 暂无视频。请先在 `自动短视频生成器` 页面生成视频。")
else:
    # 汇总信息
    total_size = format_file_size(sum(v['size'] for v in videos))
    st.caption(f"共 {len(videos)} 个视频 | 总大小 {total_size}")

    # 网格：每行3列
    grid_container = st.container(border=True)
    with grid_container:
        cols = st.columns(3)
        for idx, video in enumerate(videos):
            col = cols[idx % 3]
            with col:
                card = st.container(border=True)
                with card:
                    st.markdown(f"**{video['filename']}**")
                    st.caption(f"{video['size_formatted']} · {video['create_time_formatted']}")
                    st.video(video['filepath'])
                    btn1, btn2 = st.columns(2)
                    with btn1:
                        if st.button("▶️ 播放", key=f"grid_play_{idx}", use_container_width=True):
                            st.session_state.selected_video = video['filepath']
                            st.session_state.selected_video_name = video['filename']
                            st.toast(f"正在播放 {video['filename']}")
                    with btn2:
                        try:
                            with open(video['filepath'], 'rb') as f:
                                st.download_button(
                                    label="📥 下载",
                                    data=f.read(),
                                    file_name=video['filename'],
                                    mime="video/mp4",
                                    key=f"grid_dl_{idx}",
                                    use_container_width=True
                                )
                        except Exception:
                            st.error("下载失败")

    # 底部播放器（可选）
    if 'selected_video' in st.session_state and st.session_state.selected_video:
        st.markdown('---')
        st.markdown(f"### 🎬 正在播放: {st.session_state.get('selected_video_name', '')}")
        st.video(st.session_state.selected_video)

