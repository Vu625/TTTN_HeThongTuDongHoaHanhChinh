from services.data_viz_service import get_statistics, name_status, get_name_form
from services.layout import display_back_button
import streamlit as st
import pandas as pd
import plotly.express as px


# Gọi hàm thống kê
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

    # ===================================================
    # PHẦN 1: THỐNG KÊ THEO TRẠNG THÁI (Dịch sang Tiếng Việt)
    # ===================================================
    st.subheader("🔍 Phân bố hồ sơ theo trạng thái")
    df_status = pd.DataFrame(list(stats["by_status"].items()), columns=["Trạng thái", "Số lượng"])

    # **ÁP DỤNG HÀM name_status ĐỂ DỊCH TRẠNG THÁI**
    df_status["Trạng thái"] = df_status["Trạng thái"].apply(name_status)

    fig1 = px.bar(
        df_status,
        x="Trạng thái",
        y="Số lượng",
        color="Trạng thái",
        text_auto=True,
        title="Số lượng hồ sơ theo Trạng thái xử lý"  # Thêm tiêu đề cho biểu đồ
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ===================================================
    # PHẦN 2: THỐNG KÊ THEO THỦ TỤC (Dịch sang Tiếng Việt)
    # ===================================================
    st.subheader("📂 Thủ tục được sử dụng nhiều nhất")
    df_proc = pd.DataFrame(list(stats["by_procedure"].items()), columns=["Thủ tục ID", "Số lượng"])

    # **ÁP DỤNG HÀM get_name_form ĐỂ DỊCH TÊN THỦ TỤC**
    df_proc["Thủ tục"] = df_proc["Thủ tục ID"].apply(get_name_form)

    # Loại bỏ cột Thủ tục ID (tùy chọn)
    df_proc = df_proc.drop(columns=["Thủ tục ID"])

    fig2 = px.pie(
        df_proc,
        names="Thủ tục",
        values="Số lượng",
        title="Tỷ lệ thủ tục được sử dụng"  # Cập nhật tiêu đề
    )
    st.plotly_chart(fig2, use_container_width=True)