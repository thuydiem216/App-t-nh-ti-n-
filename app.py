
from pathlib import Path
from datetime import datetime

import streamlit as st

# ==========================================
# 1. CẤU HÌNH ỨNG DỤNG
# ==========================================
BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Tiệm trà Hoàng hôn",
    page_icon="🧋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ưu tiên logo_hoang_hon.png, nếu không có thì dùng banner.png
LOGO_PATH = BASE_DIR / "logo_hoang_hon.png"
BANNER_PATH = BASE_DIR / "banner.png"

# ==========================================
# 2. MENU VÀ BẢNG GIÁ
# ==========================================
MENU = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa trân châu đường đen": 35000,
    "Trà sữa matcha": 35000,
    "Trà sữa socola": 32000,
    "Trà sữa khoai môn": 35000,
    "Trà sữa ô long": 33000,
    "Trà đào": 30000,
    "Trà vải": 30000,
    "Trà chanh": 25000,
    "Matcha latte": 38000,
}

SIZE_PRICE = {
    "M": 0,
    "L": 10000,
    "XL": 15000,
}

TOPPING_PRICE = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 7000,
    "Thạch trái cây": 5000,
    "Pudding trứng": 7000,
    "Kem cheese": 10000,
    "Flan": 7000,
}

SUGAR_LEVELS = ["0%", "25%", "50%", "75%", "100%"]
ICE_LEVELS = ["Không đá", "Ít đá", "Bình thường", "Nhiều đá"]

# ==========================================
# 3. KHỞI TẠO DỮ LIỆU PHIÊN LÀM VIỆC
# ==========================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "customer" not in st.session_state:
    st.session_state.customer = ""

if "paid" not in st.session_state:
    st.session_state.paid = False

if "invoice_no" not in st.session_state:
    st.session_state.invoice_no = ""

if "paid_time" not in st.session_state:
    st.session_state.paid_time = ""

# ==========================================
# 4. HÀM XỬ LÝ
# ==========================================
def money(amount):
    """Định dạng tiền Việt Nam."""
    return f"{amount:,.0f} đ".replace(",", ".")


def unit_price(item):
    """Tính giá một ly, gồm giá gốc, size và topping."""
    topping_cost = sum(
        TOPPING_PRICE[topping]
        for topping in item["toppings"]
    )

    return (
        item["base_price"]
        + SIZE_PRICE[item["size"]]
        + topping_cost
    )


def item_total(item):
    """Tính thành tiền của một món."""
    return unit_price(item) * item["quantity"]


def total_amount():
    """Tính tổng tiền đơn hàng."""
    return sum(
        item_total(item)
        for item in st.session_state.cart
    )


def total_quantity():
    """Tính tổng số ly."""
    return sum(
        item["quantity"]
        for item in st.session_state.cart
    )


def receipt_text():
    """Tạo nội dung hóa đơn dạng văn bản."""
    lines = [
        "========================================",
        "          TIEM TRA HOANG HON",
        "             HOA DON BAN HANG",
        "========================================",
        f"Ma hoa don: {st.session_state.invoice_no}",
        f"Khach hang: {st.session_state.customer}",
        f"Thoi gian: {st.session_state.paid_time}",
        "----------------------------------------",
    ]

    for index, item in enumerate(
        st.session_state.cart, start=1
    ):
        toppings = ", ".join(item["toppings"]) or "Khong topping"

        lines.extend([
            f"{index}. {item['name']}",
            f"   Size: {item['size']}",
            f"   So luong: {item['quantity']}",
            f"   Duong: {item['sugar']}",
            f"   Da: {item['ice']}",
            f"   Topping: {toppings}",
            f"   Don gia: {money(unit_price(item))}",
            f"   Thanh tien: {money(item_total(item))}",
            "----------------------------------------",
        ])

    lines.extend([
        f"TONG SO LY: {total_quantity()}",
        f"TONG THANH TOAN: {money(total_amount())}",
        "Trang thai: DA THANH TOAN",
        "Cam on quy khach va hen gap lai!",
        "========================================",
    ])

    return "\n".join(lines)


# ==========================================
# 5. LOGO VÀ TIÊU ĐỀ
# ==========================================
header_left, header_right = st.columns([1, 4])

with header_left:
    if LOGO_PATH.is_file():
        st.image(str(LOGO_PATH), width=200)
    elif BANNER_PATH.is_file():
        st.image(str(BANNER_PATH), width=200)
    else:
        st.markdown("# 🧋")

with header_right:
    st.title("TIỆM TRÀ HOÀNG HÔN")
    st.subheader("Hương vị dịu dàng, khoảnh khắc hoàng hôn")
    st.caption("Ứng dụng gọi món · Tính tiền · Xuất hóa đơn")

st.divider()

# ==========================================
# 6. THÔNG TIN KHÁCH HÀNG
# ==========================================
st.header("👤 Thông tin khách hàng")

st.text_input(
    "Tên khách hàng",
    key="customer",
    placeholder="Nhập tên khách hàng...",
    disabled=st.session_state.paid,
)

# ==========================================
# 7. CHỌN ĐỒ UỐNG VÀ THÊM MÓN
# ==========================================
st.header("🥤 Menu đồ uống")

with st.form("drink_form"):
    col1, col2 = st.columns(2)

    with col1:
        drink = st.selectbox(
            "Loại đồ uống",
            options=list(MENU.keys()),
        )

        size = st.selectbox(
            "Size ly",
            options=list(SIZE_PRICE.keys()),
            format_func=lambda s: (
                f"Size {s} - "
                + (
                    "Không phụ thu"
                    if SIZE_PRICE[s] == 0
                    else f"Phụ thu {money(SIZE_PRICE[s])}"
                )
            ),
        )

        quantity = st.number_input(
            "Số lượng",
            min_value=1,
            max_value=100,
            value=1,
            step=1,
        )

    with col2:
        sugar = st.select_slider(
            "Mức độ đường",
            options=SUGAR_LEVELS,
            value="50%",
        )

        ice = st.selectbox(
            "Mức độ đá",
            options=ICE_LEVELS,
            index=2,
        )

        toppings = st.multiselect(
            "Topping thêm",
            options=list(TOPPING_PRICE.keys()),
            help="Có thể chọn nhiều topping cho mỗi ly.",
        )

    st.info(
        f"Giá gốc: {money(MENU[drink])} / ly | "
        f"Phụ thu size: {money(SIZE_PRICE[size])}"
    )

    add_button = st.form_submit_button(
        "➕ THÊM MÓN VÀO ĐƠN",
        use_container_width=True,
        disabled=st.session_state.paid,
    )

if add_button:
    if not st.session_state.customer.strip():
        st.warning("Vui lòng nhập tên khách hàng trước.")
    else:
        new_item = {
            "name": drink,
            "base_price": MENU[drink],
            "size": size,
            "quantity": int(quantity),
            "sugar": sugar,
            "ice": ice,
            "toppings": list(toppings),
        }

        st.session_state.cart.append(new_item)
        st.success(f"Đã thêm {drink} vào đơn hàng.")
        st.rerun()

# ==========================================
# 8. CHI TIẾT ĐƠN HÀNG
# ==========================================
st.divider()
st.header("🛒 Đơn hàng của khách")

if not st.session_state.cart:
    st.info("Đơn hàng đang trống. Hãy chọn đồ uống để bắt đầu.")

else:
    for index, item in enumerate(st.session_state.cart):
        with st.container(border=True):
            info_col, price_col, action_col = st.columns([5, 2, 1])

            with info_col:
                st.markdown(f"**{index + 1}. {item['name']}**")

                st.write(
                    f"Size {item['size']} · "
                    f"Số lượng: {item['quantity']}"
                )

                st.caption(
                    f"Đường: {item['sugar']} · Đá: {item['ice']}"
                )

                st.caption(
                    "Topping: "
                    + (", ".join(item["toppings"]) or "Không topping")
                )

                st.caption(
                    f"Đơn giá: {money(unit_price(item))}"
                )

            with price_col:
                st.markdown("**Thành tiền**")
                st.markdown(f"### {money(item_total(item))}")

            with action_col:
                if not st.session_state.paid:
                    if st.button(
                        "🗑️",
                        key=f"delete_{index}",
                        help="Xóa món khỏi đơn",
                    ):
                        st.session_state.cart.pop(index)
                        st.rerun()

    # Tổng kết
    st.divider()

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric("🧋 Tổng số ly", total_quantity())

    with metric2:
        st.metric("💰 Tổng thanh toán", money(total_amount()))

    # ==========================================
    # 9. THANH TOÁN
    # ==========================================
    st.divider()
    st.header("💳 Thanh toán")

    if not st.session_state.paid:
        st.write(
            f"Khách hàng: **{st.session_state.customer or 'Chưa nhập'}**"
        )

        st.write(
            f"Số tiền cần thanh toán: **{money(total_amount())}**"
        )

        if st.button(
            "✅ THANH TOÁN VÀ XUẤT HÓA ĐƠN",
            type="primary",
            use_container_width=True,
        ):
            if not st.session_state.customer.strip():
                st.error("Vui lòng nhập tên khách hàng.")

            elif not st.session_state.cart:
                st.error("Đơn hàng chưa có món.")

            else:
                now = datetime.now()

                st.session_state.invoice_no = now.strftime(
                    "HD%Y%m%d%H%M%S"
                )

                st.session_state.paid_time = now.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )

                st.session_state.paid = True
                st.rerun()

    # ==========================================
    # 10. HÓA ĐƠN SAU THANH TOÁN
    # ==========================================
    if st.session_state.paid:
        st.success("Thanh toán thành công! Hóa đơn đã được tạo.")

        st.divider()
        st.header("🧾 HÓA ĐƠN THANH TOÁN")

        st.markdown("### 🧋 TIỆM TRÀ HOÀNG HÔN")

        st.write(f"**Mã hóa đơn:** {st.session_state.invoice_no}")
        st.write(f"**Khách hàng:** {st.session_state.customer}")
        st.write(f"**Thời gian:** {st.session_state.paid_time}")
        st.write("**Trạng thái:** ĐÃ THANH TOÁN")

        invoice_rows = []

        for index, item in enumerate(
            st.session_state.cart, start=1
        ):
            invoice_rows.append({
                "STT": index,
                "Tên món": item["name"],
                "Size": item["size"],
                "Số lượng": item["quantity"],
                "Đường": item["sugar"],
                "Đá": item["ice"],
                "Topping": ", ".join(item["toppings"]) or "Không",
                "Đơn giá": money(unit_price(item)),
                "Thành tiền": money(item_total(item)),
            })

        st.dataframe(
            invoice_rows,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader(f"TỔNG TIỀN: {money(total_amount())}")
        st.write("Cảm ơn quý khách và hẹn gặp lại! ❤️")

        st.download_button(
            label="📥 TẢI HÓA ĐƠN TXT",
            data=receipt_text(),
            file_name=f"{st.session_state.invoice_no}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.caption(
            "Bạn có thể mở file TXT vừa tải về để lưu hoặc in hóa đơn."
        )

        if st.button(
            "🆕 TẠO ĐƠN HÀNG MỚI",
            use_container_width=True,
        ):
            st.session_state.cart = []
            st.session_state.customer = ""
            st.session_state.paid = False
            st.session_state.invoice_no = ""
            st.session_state.paid_time = ""
            st.rerun()

# ==========================================
# 11. CHÂN TRANG
# ==========================================
st.divider()
st.caption(
    "© Tiệm trà Hoàng hôn | Chúc bạn một ngày thật ngọt ngào 🌅"
)
