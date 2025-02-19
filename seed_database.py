import os
from app import app, db, Room

def seed_database():
    # Ensure the database and tables are created
    with app.app_context():
        db.create_all()

        print("Welcome to the Database Seeder!")
        print("You can add hotel details to the database.")

        while True:
            print("\nEnter the details for a new hotel:")
            hotel_name = input("Hotel Name: ")
            price = float(input("Price per night (e.g., 23697.0): "))
            location = input("Location (e.g., Plane in Urainen, Finland): ")
            guests = int(input("Number of guests (e.g., 8): "))

            # Input tags for the 5 images
            print("\nEnter tags for the 5 images (e.g., 'main_view', 'property_view_1', etc.):")
            image1 = input("Tag for Image 1: ")
            image2 = input("Tag for Image 2: ")
            image3 = input("Tag for Image 3: ")
            image4 = input("Tag for Image 4: ")
            image5 = input("Tag for Image 5: ")

            # Create a new Room object
            new_room = Room(
                hotel_name=hotel_name,
                price=price,
                image1=f"{image1}",
                image2=f"{image2}",
                image3=f"{image3}",
                image4=f"{image4}",
                image5=f"{image5}",
                location=location,
                guests=guests
            )

            # Add the new room to the database
            db.session.add(new_room)
            db.session.commit()

            print(f"\nSuccessfully added '{hotel_name}' to the database!")

            # Ask if the user wants to add another hotel
            another = input("\nDo you want to add another hotel? (yes/no): ").strip().lower()
            if another != "yes":
                print("\nDatabase seeding complete. Exiting...")
                break

if __name__ == "__main__":
    seed_database()