import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="ShopPulse | E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    orders = pd.read_csv("data/orders.csv")
    customers = pd.read_csv("data/customers.csv")
    products = pd.read_csv("data/products.csv")
    inventory = pd.read_csv("data/inventory.csv")

    orders["Order_Date"] = pd.to_datetime(orders["Order_Date"])

    return orders, customers, products, inventory


orders, customers, products, inventory = load_data()
# URL QUERY PARAMETERS
params = st.query_params

st.markdown("""
<style>
.stApp {
    background-color: #0B1120;
}
.block-container {
    padding-top: 1.5rem;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
[data-testid="stMetric"] {
    background-color: #151D30;
    padding: 18px;
    border: 1px solid #263247;
    border-radius: 12px;
}
[data-testid="stMetricLabel"] {
    color: #94A3B8;
}
[data-testid="stMetricValue"] {
    color: #F8FAFC;
}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("🛍️ ShopPulse")
st.sidebar.caption("E-Commerce Intelligence Platform")
st.sidebar.divider()

# PAGE NAVIGATION
pages = [
    "Overview",
    "Sales Analytics",
    "Product Analytics",
    "Customer Analytics",
    "Inventory Management",
    "Order Management"
]

page_from_url = params.get("page", "Overview")

if page_from_url not in pages:
    page_from_url = "Overview"

page = st.sidebar.radio(
    "Navigation",
    pages,
    index=pages.index(page_from_url),
    key="page_navigation"
)

st.query_params["page"] = page

st.sidebar.divider()
st.sidebar.subheader("GLOBAL FILTERS")

regions = ["South", "North", "East", "West"]
categories = [
    "Electronics", "Fashion", "Home & Kitchen",
    "Beauty", "Sports"
]
statuses = [
    "Delivered", "Shipped", "Processing",
    "Cancelled", "Returned"
]

# REGION FILTER WITH URL SUPPORT
region_from_url = params.get_all("region")

if not region_from_url:
    region_from_url = regions

region_from_url = [
    r for r in region_from_url if r in regions
]

selected_region = st.sidebar.multiselect(
    "Region",
    regions,
    default=region_from_url,
    key="region_filter"
)

st.query_params["region"] = selected_region

selected_category = st.sidebar.multiselect(
    "Category", categories, default=categories
)

selected_status = st.sidebar.multiselect(
    "Order Status", statuses, default=statuses
)

st.sidebar.divider()
st.sidebar.caption("ShopPulse Dashboard v1.0")

# HEADER
col1, col2 = st.columns([4, 1])

with col1:
    st.title("E-Commerce Operations")
    st.caption(
        "Monitor business performance, products, "
        "customers and operations."
    )

with col2:
    st.success("● SYSTEM ONLINE")

st.divider()

# DATE FILTERS
st.subheader("Dashboard Controls")

c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    start_date = st.date_input(
        "Start Date", value=date(2025, 1, 1)
    )

with c2:
    end_date = st.date_input(
        "End Date", value=date(2025, 12, 31)
    )

with c3:
    st.write("")
    st.write("")
    if st.button("↻ Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# APPLY FILTERS
filtered_orders = orders.copy()

filtered_orders = filtered_orders[
    (filtered_orders["Order_Date"].dt.date >= start_date) &
    (filtered_orders["Order_Date"].dt.date <= end_date)
]

filtered_orders = filtered_orders[
    filtered_orders["Region"].isin(selected_region) &
    filtered_orders["Category"].isin(selected_category) &
    filtered_orders["Order_Status"].isin(selected_status)
]

st.divider()

# OVERVIEW PAGE
if page == "Overview":

    st.subheader("Business Overview")
    st.caption("Your complete business performance at a glance.")

    st.markdown("### Key Performance Indicators")

    
    total_revenue = filtered_orders["Revenue"].sum()
    total_orders = filtered_orders["Order_ID"].nunique()
    total_profit = filtered_orders["Profit"].sum()
    total_customers = filtered_orders["Customer_ID"].nunique()

    cols = st.columns(4)

    with cols[0]:
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")

    with cols[1]:
        st.metric("Total Orders", f"{total_orders:,}")

    with cols[2]:
        st.metric("Total Profit", f"₹{total_profit:,.2f}")

    with cols[3]:
        st.metric("Customers", f"{total_customers:,}")

    st.markdown("### Business Performance")

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown("#### Revenue Trend")

            monthly_revenue = (
                filtered_orders
                .groupby(filtered_orders["Order_Date"].dt.to_period("M"))["Revenue"]
                .sum()
                .reset_index()
            )

            monthly_revenue["Month"] = monthly_revenue["Order_Date"].astype(str)

            fig=px.line(
                monthly_revenue,
                x="Month",
                y="Revenue",
                markers=True,
                title="Monthly Revenue",
                template="plotly_dark"
            )

            fig.update_layout(
                paper_bgcolor="#151D30",
                plot_bgcolor="#151D30",
                font_color="#F8FAFC"
            )

            st.plotly_chart(fig, use_container_width=True)


    with right:
        with st.container(border=True):
            st.markdown("#### Category Performance")

            category_sales = (
                filtered_orders.groupby("Category")["Revenue"]
                .sum()
                .reset_index()
                .sort_values("Revenue", ascending=False)
            )

            fig = px.bar(
                category_sales,
                x="Category",
                y="Revenue",
                color="Category",
                title="Revenue by Category",
                template="plotly_dark",
                text_auto=".2s"
            )

            fig.update_layout(
                paper_bgcolor="#151D30",
                plot_bgcolor="#151D30",
                font_color="#F8FAFC",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)


    left, right = st.columns(2)

    
    with left:
        with st.container(border=True):
            st.markdown("#### Regional Sales")

            regional_sales = (
                filtered_orders.groupby("Region")["Revenue"]
                .sum()
                .reset_index()
                .sort_values("Revenue", ascending=False)
            )

            fig = px.pie(
                regional_sales,
                names="Region",
                values="Revenue",
                title="Revenue Distribution by Region",
                hole=0.45,
                template="plotly_dark"
            )

            fig.update_layout(
                paper_bgcolor="#151D30",
                font_color="#F8FAFC"
            )

            st.plotly_chart(fig, use_container_width=True)


    
    with right:
        with st.container(border=True):
            st.markdown("#### Order Status")

            status_data = (
                filtered_orders.groupby("Order_Status")["Order_ID"]
                .nunique()
                .reset_index(name="Orders")
            )

            fig = px.bar(
                status_data,
                x="Order_Status",
                y="Orders",
                color="Order_Status",
                title="Orders by Status",
                template="plotly_dark",
                text_auto=True
            )

            fig.update_layout(
                paper_bgcolor="#151D30",
                plot_bgcolor="#151D30",
                font_color="#F8FAFC",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)


# OTHER PAGES

elif page == "Sales Analytics":
    st.title("📈 Sales Analytics")
    st.caption("Explore revenue, profit, orders and sales performance.")

    if filtered_orders.empty:
        st.warning("No sales data available for the selected filters.")

    else:
        # SALES KPIs
        total_revenue = filtered_orders["Revenue"].sum()
        total_profit = filtered_orders["Profit"].sum()
        total_orders = filtered_orders["Order_ID"].nunique()
        total_quantity = filtered_orders["Quantity"].sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        c2.metric("Total Profit", f"₹{total_profit:,.2f}")
        c3.metric("Total Orders", f"{total_orders:,}")
        c4.metric("Units Sold", f"{total_quantity:,}")

        st.divider()

        # MONTHLY SALES TREND
        st.subheader("Monthly Sales Trend")

        monthly_sales = filtered_orders.copy()
        monthly_sales["Month"] = monthly_sales["Order_Date"].dt.to_period("M").astype(str)

        monthly_data = monthly_sales.groupby("Month", as_index=False).agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum")
        )

        fig = px.line(
            monthly_data,
            x="Month",
            y=["Revenue", "Profit"],
            markers=True,
            title="Monthly Revenue and Profit"
        )

        st.plotly_chart(fig, use_container_width=True)

        # REGION AND PAYMENT ANALYSIS
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sales by Region")

            region_data = filtered_orders.groupby("Region", as_index=False)["Revenue"].sum()

            fig = px.bar(
                region_data,
                x="Region",
                y="Revenue",
                color="Region",
                title="Revenue by Region"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Payment Method Analysis")

            payment_data = filtered_orders.groupby(
                "Payment_Method",
                as_index=False
            )["Revenue"].sum()

            fig = px.pie(
                payment_data,
                names="Payment_Method",
                values="Revenue",
                hole=0.45,
                title="Revenue by Payment Method"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ORDER STATUS ANALYSIS
        st.subheader("Order Status Analysis")

        status_data = filtered_orders.groupby(
            "Order_Status",
            as_index=False
        ).agg(
            Orders=("Order_ID", "nunique"),
            Revenue=("Revenue", "sum")
        )

        fig = px.bar(
            status_data,
            x="Order_Status",
            y="Orders",
            color="Order_Status",
            title="Orders by Status"
        )

        st.plotly_chart(fig, use_container_width=True)

        # SALES DATA TABLE
        st.subheader("Sales Performance Data")

        st.dataframe(
            monthly_data,
            use_container_width=True,
            hide_index=True
        )



elif page == "Product Analytics":
    st.title("📦 Product Analytics")
    st.caption("Analyze product performance, revenue and profitability.")

    if filtered_orders.empty:
        st.warning("No product data available for the selected filters.")

    else:
        # PRODUCT PERFORMANCE
        product_data = filtered_orders.groupby(
            ["Product_ID", "Product_Name", "Category"],
            as_index=False
        ).agg(
            Units_Sold=("Quantity", "sum"),
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order_ID", "nunique")
        )

        # PRODUCT KPIs
        total_products = product_data["Product_ID"].nunique()
        total_units = product_data["Units_Sold"].sum()
        total_revenue = product_data["Revenue"].sum()
        total_profit = product_data["Profit"].sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Products Sold", f"{total_products:,}")
        c2.metric("Units Sold", f"{total_units:,}")
        c3.metric("Product Revenue", f"₹{total_revenue:,.2f}")
        c4.metric("Product Profit", f"₹{total_profit:,.2f}")

        st.divider()

        # TOP PRODUCTS BY REVENUE
        st.subheader("Top 10 Products by Revenue")

        top_products = product_data.nlargest(10, "Revenue")

        fig = px.bar(
            top_products.sort_values("Revenue"),
            x="Revenue",
            y="Product_Name",
            orientation="h",
            color="Revenue",
            title="Top 10 Revenue-Generating Products"
        )

        st.plotly_chart(fig, use_container_width=True)

        # CATEGORY ANALYSIS
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Revenue by Category")

            category_revenue = product_data.groupby(
                "Category",
                as_index=False
            )["Revenue"].sum()

            fig = px.pie(
                category_revenue,
                names="Category",
                values="Revenue",
                hole=0.45,
                title="Category Revenue Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Profit by Category")

            category_profit = product_data.groupby(
                "Category",
                as_index=False
            )["Profit"].sum()

            fig = px.bar(
                category_profit,
                x="Category",
                y="Profit",
                color="Category",
                title="Category-wise Profit"
            )

            st.plotly_chart(fig, use_container_width=True)

        # TOP PRODUCTS BY QUANTITY
        st.subheader("Best-Selling Products")

        top_selling = product_data.nlargest(10, "Units_Sold")

        fig = px.bar(
            top_selling.sort_values("Units_Sold"),
            x="Units_Sold",
            y="Product_Name",
            orientation="h",
            color="Units_Sold",
            title="Top 10 Products by Units Sold"
        )

        st.plotly_chart(fig, use_container_width=True)

        # PRODUCT DATA TABLE
        st.subheader("Complete Product Performance")

        st.dataframe(
            product_data.sort_values("Revenue", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        # DOWNLOAD REPORT
        st.download_button(
            label="⬇️ Download Product Analytics CSV",
            data=product_data.to_csv(index=False).encode("utf-8"),
            file_name="shoppulse_product_analytics.csv",
            mime="text/csv"
        )



elif page == "Customer Analytics":
    st.title("👥 Customer Analytics")
    st.caption("Understand customer behavior, spending and purchase patterns.")

    if filtered_orders.empty:
        st.warning("No customer data available for the selected filters.")

    else:
        # CUSTOMER PERFORMANCE
        customer_data = filtered_orders.groupby(
            "Customer_ID",
            as_index=False
        ).agg(
            Orders=("Order_ID", "nunique"),
            Total_Spent=("Revenue", "sum"),
            Total_Profit=("Profit", "sum"),
            Units_Purchased=("Quantity", "sum")
        )

        # CUSTOMER KPIs
        total_customers = customer_data["Customer_ID"].nunique()
        repeat_customers = (customer_data["Orders"] > 1).sum()
        average_spending = customer_data["Total_Spent"].mean()
        average_orders = customer_data["Orders"].mean()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Customers", f"{total_customers:,}")
        c2.metric("Repeat Customers", f"{repeat_customers:,}")
        c3.metric("Average Spending", f"₹{average_spending:,.2f}")
        c4.metric("Avg. Orders / Customer", f"{average_orders:.2f}")

        st.divider()

        # TOP CUSTOMERS
        st.subheader("Top 10 Customers by Spending")

        top_customers = customer_data.nlargest(10, "Total_Spent")

        fig = px.bar(
            top_customers.sort_values("Total_Spent"),
            x="Total_Spent",
            y="Customer_ID",
            orientation="h",
            color="Total_Spent",
            title="Top 10 Highest-Spending Customers"
        )

        st.plotly_chart(fig, use_container_width=True)

        # CUSTOMER PURCHASE BEHAVIOR
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Customer Purchase Frequency")

            frequency_data = customer_data.copy()

            frequency_data["Purchase_Type"] = frequency_data[
                "Orders"
            ].apply(
                lambda x: "Repeat Customer" if x > 1 else "One-time Customer"
            )

            frequency_summary = frequency_data.groupby(
                "Purchase_Type",
                as_index=False
            ).size()

            fig = px.pie(
                frequency_summary,
                names="Purchase_Type",
                values="size",
                hole=0.45,
                title="One-time vs Repeat Customers"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Customer Distribution by Region")

            region_customers = filtered_orders.groupby(
                "Region",
                as_index=False
            )["Customer_ID"].nunique()

            fig = px.bar(
                region_customers,
                x="Region",
                y="Customer_ID",
                color="Region",
                title="Unique Customers by Region"
            )

            st.plotly_chart(fig, use_container_width=True)

        # CUSTOMER SPENDING DISTRIBUTION
        st.subheader("Customer Spending Distribution")

        fig = px.histogram(
            customer_data,
            x="Total_Spent",
            nbins=20,
            title="Distribution of Customer Spending"
        )

        st.plotly_chart(fig, use_container_width=True)

        # CUSTOMER TABLE
        st.subheader("Customer Performance Details")

        st.dataframe(
            customer_data.sort_values(
                "Total_Spent",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        # DOWNLOAD REPORT
        st.download_button(
            label="⬇️ Download Customer Analytics CSV",
            data=customer_data.to_csv(index=False).encode("utf-8"),
            file_name="shoppulse_customer_analytics.csv",
            mime="text/csv"
        )



elif page == "Inventory Management":

    st.title("🏬 Inventory Management")
    st.caption("Monitor stock levels, product availability and inventory value.")

    st.divider()

    # INVENTORY FILTERS
    search_product = st.text_input(
        "🔍 Search Product",
        placeholder="Enter product name or Product ID"
    )

    stock_data = inventory.copy()

    stock_categories = st.multiselect(
        "Filter by Category",
        sorted(stock_data["Category"].unique()),
        default=sorted(stock_data["Category"].unique())
    )

    stock_data = stock_data[
        stock_data["Category"].isin(stock_categories)
    ]

    if search_product:
        mask = (
            stock_data["Product_Name"].str.contains(
                search_product, case=False, na=False
            ) |
            stock_data["Product_ID"].str.contains(
                search_product, case=False, na=False
            )
        )
        stock_data = stock_data[mask]

    # INVENTORY KPIs
    total_products = stock_data["Product_ID"].nunique()
    total_stock = stock_data["Current_Stock"].sum()
    low_stock = (stock_data["Stock_Status"] == "Low Stock").sum()
    out_of_stock = (stock_data["Current_Stock"] == 0).sum()
    inventory_value = stock_data["Stock_Value"].sum()

    st.markdown("### Inventory Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Products", f"{total_products:,}")
    c2.metric("Available Units", f"{total_stock:,}")
    c3.metric("Low Stock Products", f"{low_stock:,}")
    c4.metric("Out of Stock", f"{out_of_stock:,}")

    st.metric("Total Inventory Value", f"₹{inventory_value:,.2f}")

    st.divider()

    # INVENTORY CHARTS
    st.markdown("### Stock Analysis")

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown("#### Stock by Category")

            category_stock = (
                stock_data.groupby("Category")["Current_Stock"]
                .sum()
                .reset_index()
                .sort_values("Current_Stock", ascending=False)
            )

            fig = px.bar(
                category_stock,
                x="Category",
                y="Current_Stock",
                color="Category",
                title="Available Units by Category",
                template="plotly_dark",
                text_auto=True
            )

            fig.update_layout(
                paper_bgcolor="#151D30",
                plot_bgcolor="#151D30",
                font_color="#F8FAFC",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

    with right:
        with st.container(border=True):
            st.markdown("#### Stock Status Distribution")

            status_data = stock_data.copy()

            status_data.loc[
                status_data["Current_Stock"] == 0,
                "Display_Status"
            ] = "Out of Stock"

            status_data.loc[
                (status_data["Current_Stock"] > 0) &
                (status_data["Stock_Status"] == "Low Stock"),
                "Display_Status"
            ] = "Low Stock"

            status_data.loc[
                (status_data["Current_Stock"] > 0) &
                (status_data["Stock_Status"] != "Low Stock"),
                "Display_Status"
            ] = "Healthy"

            status_summary = (
                status_data["Display_Status"]
                .value_counts()
                .reset_index()
            )

            status_summary.columns = ["Stock_Status", "Products"]

            fig = px.pie(
                status_summary,
                names="Stock_Status",
                values="Products",
                hole=0.45,
                title="Product Stock Status",
                template="plotly_dark"
            )

            fig.update_layout(
                paper_bgcolor="#151D30",
                font_color="#F8FAFC"
            )

            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # LOW STOCK ALERTS
    st.markdown("### ⚠️ Low Stock Alerts")

    low_stock_data = stock_data[
        (stock_data["Stock_Status"] == "Low Stock") &
        (stock_data["Current_Stock"] > 0)
    ]

    if not low_stock_data.empty:
        st.warning(f"{len(low_stock_data)} products need stock replenishment.")

        st.dataframe(
            low_stock_data[
                [
                    "Product_ID",
                    "Product_Name",
                    "Current_Stock",
                    "Reorder_Level",
                    "Stock_Status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No low-stock products found in the selected filters.")

    st.divider()

    # COMPLETE INVENTORY TABLE
    st.markdown("### Complete Inventory")

    st.dataframe(
        stock_data.sort_values(
            "Current_Stock", ascending=True
        ),
        use_container_width=True,
        hide_index=True,
        height=400
    )


elif page == "Order Management":

    st.title("🧾 Order Management")
    st.caption("Search, explore and inspect customer orders.")

    st.divider()

    # SEARCH
    search = st.text_input(
        "🔍 Search Orders",
        placeholder="Enter Order ID, Customer ID or Product Name"
    )

    # SORTING
    sort_option = st.selectbox(
        "Sort Orders By",
        ["Newest First", "Oldest First", "Highest Revenue", "Lowest Revenue"]
    )

    order_data = filtered_orders.copy()

    if search:
        mask = (
            order_data["Order_ID"].astype(str).str.contains(search, case=False, na=False) |
            order_data["Customer_ID"].astype(str).str.contains(search, case=False, na=False) |
            order_data["Product_Name"].astype(str).str.contains(search, case=False, na=False)
        )
        order_data = order_data[mask]

    if sort_option == "Newest First":
        order_data = order_data.sort_values("Order_Date", ascending=False)

    elif sort_option == "Oldest First":
        order_data = order_data.sort_values("Order_Date", ascending=True)

    elif sort_option == "Highest Revenue":
        order_data = order_data.sort_values("Revenue", ascending=False)

    else:
        order_data = order_data.sort_values("Revenue", ascending=True)

    # SUMMARY
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Order Records", f"{len(order_data):,}")

    with c2:
        st.metric("Unique Orders", f"{order_data['Order_ID'].nunique():,}")

    with c3:
        st.metric("Filtered Revenue", f"₹{order_data['Revenue'].sum():,.2f}")

    st.divider()

    # ORDER TABLE
    st.subheader("Order Records")

    display_columns = [
        "Order_ID",
        "Order_Date",
        "Customer_ID",
        "Product_Name",
        "Quantity",
        "Revenue",
        "Profit",
        "Region",
        "Order_Status"
    ]

    
    # PAGINATION
    st.markdown("#### Browse Orders")

    page_size = st.selectbox(
        "Records per page",
        [10, 25, 50, 100],
        index=1
    )

    total_records = len(order_data)
    total_pages = max(1, (total_records + page_size - 1) // page_size)

    current_page = st.selectbox(
        "Select Page",
        range(1, total_pages + 1)
    )

    start_index = (current_page - 1) * page_size
    end_index = start_index + page_size

    page_data = order_data.iloc[start_index:end_index]

    st.caption(
        f"Showing {start_index + 1 if total_records else 0} "
        f"to {min(end_index, total_records)} "
        f"of {total_records:,} records"
    )

    st.dataframe(
        page_data[display_columns],
        use_container_width=True,
        hide_index=True,
        height=400
    )


    # ORDER DETAILS
    st.divider()
    st.subheader("Order Details")

    order_ids = sorted(order_data["Order_ID"].unique().tolist())

    if order_ids:

        selected_order = st.selectbox(
            "Select an Order ID",
            order_ids
        )

        details = order_data[
            order_data["Order_ID"] == selected_order
        ]

        d1, d2, d3 = st.columns(3)

        with d1:
            st.metric(
                "Customer ID",
                details["Customer_ID"].iloc[0]
            )

        with d2:
            st.metric(
                "Total Revenue",
                f"₹{details['Revenue'].sum():,.2f}"
            )

        with d3:
            st.metric(
                "Total Profit",
                f"₹{details['Profit'].sum():,.2f}"
            )

        st.markdown("#### Products in this Order")

        st.dataframe(
            details[
                [
                    "Product_Name",
                    "Quantity",
                    "Unit_Price",
                    "Discount_Amount",
                    "Revenue",
                    "Profit"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Order Date: {details['Order_Date'].iloc[0].date()} | "
            f"Status: {details['Order_Status'].iloc[0]}"
        )

    else:
        st.warning("No orders found for the selected filters.")


st.divider()
st.caption("© 2026 ShopPulse | E-Commerce & Product Operations Dashboard")
