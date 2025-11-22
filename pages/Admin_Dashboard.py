from services.data_viz_service import get_statistics
from services.layout import display_back_button
import streamlit as st
import pandas as pd
import plotly.express as px
stats = get_statistics()
display_back_button()
if not stats:
        st.info("Chưa có dữ liệu hồ sơ để thống kê.")
else:
        st.subheader("📊 Thống kê tổng quan")
        col1, col2 = st.columns(2)
        col1.metric("Tổng số hồ sơ", stats["total"])
        col2.metric("Số thủ tục", len(stats["by_procedure"]))

        st.divider()

        st.subheader("🔍 Phân bố hồ sơ theo trạng thái")
        df_status = pd.DataFrame(list(stats["by_status"].items()), columns=["Trạng thái", "Số lượng"])
        fig1 = px.bar(df_status, x="Trạng thái", y="Số lượng", color="Trạng thái", text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📂 Thủ tục được sử dụng nhiều nhất")
        df_proc = pd.DataFrame(list(stats["by_procedure"].items()), columns=["Thủ tục", "Số lượng"])
        fig2 = px.pie(df_proc, names="Thủ tục", values="Số lượng", title="Tỷ lệ thủ tục")
        st.plotly_chart(fig2, use_container_width=True)