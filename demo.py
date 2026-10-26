from food_delivery import Customer, DeliveryPartner, MenuItem, Restaurant

# 1. Register customer Priya
priya = Customer("Priya", "9876543210", "Bangalore")
print("--- Customer registered ---")
priya.display_profile()

# 2. Register delivery partner Rajesh (phone number is a placeholder)
rajesh = DeliveryPartner("Rajesh", "9123456780", "Bike")
print("\n--- Delivery partner registered ---")
rajesh.display_profile()

# 3. Create restaurant Bawarchi and add Biryani and Kebab
bawarchi = Restaurant("Bawarchi", "MG Road")
biryani = MenuItem("Biryani", 250, False)
kebab = MenuItem("Kebab", 150, False)
bawarchi.add_item(biryani)
bawarchi.add_item(kebab)

print(f"\n--- {bawarchi.name}, {bawarchi.location} (open: {bawarchi.is_open()}) ---")
for item in bawarchi.get_menu():
    print(f"{item.name}: Rs.{item.price} ({'Veg' if item.is_veg else 'Non-veg'})")

# 4. Top up Priya's wallet by 500, then attempt -100
print("\n--- Wallet ---")
priya.add_to_wallet(500)
print("After +500:", priya._wallet_balance)
priya.add_to_wallet(-100)
print("After -100 (should be rejected):", priya._wallet_balance)

# 5. Priya places an order for Biryani and Kebab
print("\n--- Placing order ---")
order = priya.place_order(bawarchi, [biryani, kebab])

# Fix the OTP so the demo can deliver with 1234 (it is random by default)
order._otp = 1234

# 6. Bill breakdown and estimated time
subtotal = sum(item.price for item in order._items)
gst = subtotal * 0.05
packaging_fee = 20
total = order.calculate_bill()

print("\n--- Bill ---")
print(f"Subtotal:      Rs.{subtotal:.2f}")
print(f"GST (5%):      Rs.{gst:.2f}")
print(f"Packaging fee: Rs.{packaging_fee:.2f}")
print(f"Total:         Rs.{total:.2f}")
print(f"Estimated delivery time: {order.estimated_time()} minutes")

# 7. Rajesh accepts, wrong OTP, then correct OTP
print("\n--- Delivery ---")
rajesh.accept_order(order)
print("Status:", order._status, "| Rajesh available:", rajesh.is_available)

rajesh.deliver(order, 9999)
print("After wrong OTP 9999 -> status:", order._status)

rajesh.deliver(order, 1234)
print("After correct OTP 1234 -> status:", order._status,
      "| Rajesh available:", rajesh.is_available)

# 8. Notifications
print("\n--- Notifications ---")
priya.notify("Order delivered")
rajesh.notify("Order delivered")
