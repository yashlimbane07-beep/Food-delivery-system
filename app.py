import streamlit as st
from food_delivery import Customer, DeliveryPartner, MenuItem, Restaurant

st.set_page_config(page_title="Food Delivery", page_icon="🍔")
st.title("🍔 Food Delivery App")


# ---------- Session state setup ----------
def init_state():
    if "restaurant" not in st.session_state:
        r = Restaurant("Spice Garden", "Aurangabad")
        r.add_item(MenuItem("Paneer Tikka", 220, True))
        r.add_item(MenuItem("Veg Biryani", 180, True))
        r.add_item(MenuItem("Chicken Biryani", 260, False))
        r.add_item(MenuItem("Butter Naan", 40, True))
        st.session_state.restaurant = r
    st.session_state.setdefault("customers", {})   # name -> Customer
    st.session_state.setdefault("partners", {})    # name -> DeliveryPartner
    st.session_state.setdefault("orders", {})      # order_id -> (Order, customer_name)
    st.session_state.setdefault("assigned", {})    # order_id -> partner name


init_state()
S = st.session_state

section = st.sidebar.radio(
    "Go to",
    [
        "1. Create Customer",
        "2. Add Wallet Balance",
        "3. Restaurant Menu",
        "4. Place Order",
        "5. Create Delivery Partner",
        "6. Accept Order",
        "7. Enter OTP & Deliver",
    ],
)


def order_label(oid):
    order, cust = S.orders[oid]
    return f"Order #{oid} | {cust} | ₹{order.calculate_bill():.2f} | {order._status}"


# ---------- 1. Create customer ----------
if section.startswith("1"):
    st.header("Create Customer")
    with st.form("customer_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        address = st.text_input("Address")
        if st.form_submit_button("Create"):
            if not (name and phone and address):
                st.error("Please fill in all fields.")
            elif name in S.customers:
                st.error("A customer with this name already exists.")
            else:
                S.customers[name] = Customer(name, phone, address)
                st.success(f"Customer '{name}' created.")

    if S.customers:
        st.subheader("Customers")
        st.table([
            {"Name": c._name, "Phone": c._phone, "Address": c.address,
             "Wallet (₹)": c._wallet_balance}
            for c in S.customers.values()
        ])

# ---------- 2. Wallet ----------
elif section.startswith("2"):
    st.header("Add Wallet Balance")
    if not S.customers:
        st.info("Create a customer first.")
    else:
        name = st.selectbox("Customer", list(S.customers))
        amount = st.number_input("Amount (₹)", min_value=0, step=50, value=100)
        if st.button("Add to wallet"):
            S.customers[name].add_to_wallet(amount)
            st.success(f"Added ₹{amount}.")
        st.metric("Wallet balance", f"₹{S.customers[name]._wallet_balance}")

# ---------- 3. Menu ----------
elif section.startswith("3"):
    r = S.restaurant
    st.header(f"{r.name} — Menu")
    st.caption(f"{r.location} • {'Open' if r.is_open() else 'Closed'}")
    st.table([
        {"Item": i.name, "Price (₹)": i.price, "Type": "🟢 Veg" if i.is_veg else "🔴 Non-veg"}
        for i in r.get_menu()
    ])

# ---------- 4. Place order ----------
elif section.startswith("4"):
    st.header("Place Order")
    if not S.customers:
        st.info("Create a customer first.")
    else:
        r = S.restaurant
        menu = {i.name: i for i in r.get_menu()}
        name = st.selectbox("Customer", list(S.customers))
        chosen = st.multiselect("Items", list(menu))
        if chosen:
            items = [menu[n] for n in chosen]
            subtotal = sum(i.price for i in items)
            st.write(f"Subtotal: ₹{subtotal}")
        if st.button("Place order"):
            if not chosen:
                st.error("Select at least one item.")
            else:
                order = S.customers[name].place_order(r, items)
                S.orders[order._order_id] = (order, name)
                st.success(f"Order #{order._order_id} placed!")
                st.info(f"Your OTP: **{order._otp}** (share with the delivery partner)")
                st.write(f"Total bill (incl. 5% GST + ₹20 packaging): "
                         f"₹{order.calculate_bill():.2f}")
                st.write(f"Estimated time: {order.estimated_time()} minutes")

# ---------- 5. Create delivery partner ----------
elif section.startswith("5"):
    st.header("Create Delivery Partner")
    with st.form("partner_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        vehicle = st.selectbox("Vehicle", ["Bike", "Scooter", "Bicycle"])
        if st.form_submit_button("Create"):
            if not (name and phone):
                st.error("Please fill in all fields.")
            elif name in S.partners:
                st.error("A partner with this name already exists.")
            else:
                S.partners[name] = DeliveryPartner(name, phone, vehicle)
                st.success(f"Delivery partner '{name}' created.")

    if S.partners:
        st.subheader("Delivery partners")
        st.table([
            {"Name": p._name, "Phone": p._phone, "Vehicle": p.vehicle,
             "Available": p.is_available, "Rating": p.rating}
            for p in S.partners.values()
        ])

# ---------- 6. Accept order ----------
elif section.startswith("6"):
    st.header("Accept Order")
    pending = [oid for oid, (o, _) in S.orders.items() if o._status == "Placed"]
    available = [n for n, p in S.partners.items() if p.is_available]

    if not pending:
        st.info("No orders waiting to be accepted.")
    elif not available:
        st.info("No available delivery partners. Create one first.")
    else:
        oid = st.selectbox("Order", pending, format_func=order_label)
        partner_name = st.selectbox("Delivery partner", available)
        if st.button("Accept order"):
            S.partners[partner_name].accept_order(S.orders[oid][0])
            S.assigned[oid] = partner_name
            st.success(f"{partner_name} accepted order #{oid}.")
            customer = S.customers[S.orders[oid][1]]
            customer.notify(f"Order #{oid} accepted by {partner_name}")

# ---------- 7. OTP & deliver ----------
elif section.startswith("7"):
    st.header("Enter OTP & Complete Delivery")
    in_transit = [oid for oid, (o, _) in S.orders.items() if o._status == "Accepted"]

    if not in_transit:
        st.info("No accepted orders awaiting delivery.")
    else:
        oid = st.selectbox("Order", in_transit, format_func=order_label)
        partner = S.partners[S.assigned[oid]]
        st.write(f"Delivery partner: **{partner._name}**")
        otp_text = st.text_input("Customer OTP", max_chars=4)
        if st.button("Complete delivery"):
            order = S.orders[oid][0]
            if not otp_text.isdigit():
                st.error("OTP must be a 4-digit number.")
            else:
                partner.deliver(order, int(otp_text))
                if order._status == "Delivered":
                    st.success(f"Order #{oid} delivered! 🎉")
                    st.balloons()
                else:
                    st.error("Wrong OTP. Please try again.")

# ---------- Order overview ----------
if S.orders:
    st.divider()
    st.subheader("All orders")
    st.table([
        {"Order": oid, "Customer": cust, "Total (₹)": round(o.calculate_bill(), 2),
         "Status": o._status, "Partner": S.assigned.get(oid, "-")}
        for oid, (o, cust) in S.orders.items()
    ])
