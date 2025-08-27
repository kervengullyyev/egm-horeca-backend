from sqlalchemy.orm import Session
from app import crud, schemas, database
from app.database import get_session_local

def seed_database():
    """Seed the database with initial data"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        # Create the specific tableware categories
        categories_data = [
            {
                "name_en": "Plates",
                "name_ro": "Farfurii",
                "slug": "plates",
                "description_en": "Professional dinner plates and serving dishes",
                "description_ro": "Farfurii profesionale pentru cină și servire",
                "image_url": ""
            },
            {
                "name_en": "Cups",
                "name_ro": "Căni",
                "slug": "cups",
                "description_en": "Professional cups and drinking vessels",
                "description_ro": "Căni profesionale și vase pentru băuturi",
                "image_url": ""
            },
            {
                "name_en": "Salad Bowls",
                "name_ro": "Boluri pentru Salate",
                "slug": "salad-bowls",
                "description_en": "Professional salad bowls and mixing bowls",
                "description_ro": "Boluri profesionale pentru salate și amestecare",
                "image_url": ""
            },
            {
                "name_en": "Mugs",
                "name_ro": "Căni Mari",
                "slug": "mugs",
                "description_en": "Professional coffee mugs and tea cups",
                "description_ro": "Căni mari profesionale pentru cafea și ceai",
                "image_url": ""
            },
            {
                "name_en": "Sauciers",
                "name_ro": "Sosnițe",
                "slug": "sauciers",
                "description_en": "Professional sauce boats and gravy boats",
                "description_ro": "Sosnițe profesionale pentru sosuri și zeamă",
                "image_url": ""
            },
            {
                "name_en": "Cutlery",
                "name_ro": "Tăvițe",
                "slug": "cutlery",
                "description_en": "Professional knives, forks, and spoons",
                "description_ro": "Cuțite, furculițe și linguri profesionale",
                "image_url": ""
            },
            {
                "name_en": "Pots",
                "name_ro": "Oale",
                "slug": "pots",
                "description_en": "Professional cooking pots and saucepans",
                "description_ro": "Oale profesionale pentru gătit",
                "image_url": ""
            },
            {
                "name_en": "Teapots",
                "name_ro": "Ceainice",
                "slug": "teapots",
                "description_en": "Professional teapots and tea accessories",
                "description_ro": "Ceainice profesionale și accesorii pentru ceai",
                "image_url": ""
            },
            {
                "name_en": "Pans",
                "name_ro": "Tigăi",
                "slug": "pans",
                "description_en": "Professional frying pans and skillets",
                "description_ro": "Tigăi profesionale pentru prăjit",
                "image_url": ""
            },
            {
                "name_en": "Deals",
                "name_ro": "Oferte",
                "slug": "deals",
                "description_en": "Special offers and discounted items",
                "description_ro": "Oferte speciale și produse reduse",
                "image_url": ""
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category = crud.create_category(db, schemas.CategoryCreate(**cat_data))
            categories.append(category)
            print(f"Created category: {category.name_en}")
        
        # Create sample products for each category
        products_data = [
            {
                "name_en": "Professional Dinner Plates Set",
                "name_ro": "Set Farfurii Profesionale pentru Cină",
                "slug": "professional-dinner-plates-set",
                "description_en": "High-quality professional dinner plates set for restaurants",
                "description_ro": "Set de farfurii profesionale de înaltă calitate pentru restaurante",
                "short_description_en": "Premium dinner plates for restaurants",
                "short_description_ro": "Farfurii premium pentru restaurante",
                "price": 89.99,
                "category_id": categories[0].id,  # Plates
                "brand": "EGM",
                "sku": "PLT-001",
                "stock_quantity": 50,
                "images": []
            },
            {
                "name_en": "Professional Coffee Cups Set",
                "name_ro": "Set Căni Profesionale pentru Cafea",
                "slug": "professional-coffee-cups-set",
                "description_en": "Professional coffee cups for cafes and restaurants",
                "description_ro": "Căni profesionale pentru cafenele și restaurante",
                "short_description_en": "Professional coffee cups for cafes",
                "short_description_ro": "Căni profesionale pentru cafenele",
                "price": 45.99,
                "category_id": categories[1].id,  # Cups
                "brand": "EGM",
                "sku": "CUP-001",
                "stock_quantity": 100,
                "images": []
            },
            {
                "name_en": "Professional Salad Bowls Set",
                "name_ro": "Set Boluri Profesionale pentru Salate",
                "slug": "professional-salad-bows-set",
                "description_en": "Professional salad bowls for restaurants",
                "description_ro": "Boluri profesionale pentru restaurante",
                "short_description_en": "Professional salad bowls for restaurants",
                "short_description_ro": "Boluri profesionale pentru restaurante",
                "price": 65.99,
                "category_id": categories[2].id,  # Salad Bowls
                "brand": "EGM",
                "sku": "SAL-001",
                "stock_quantity": 30,
                "images": []
            },
            {
                "name_en": "Professional Coffee Mugs Set",
                "name_ro": "Set Căni Mari Profesionale pentru Cafea",
                "slug": "professional-coffee-mugs-set",
                "description_en": "Large professional coffee mugs for cafes",
                "description_ro": "Căni mari profesionale pentru cafenele",
                "short_description_en": "Large coffee mugs for cafes",
                "short_description_ro": "Căni mari pentru cafenele",
                "price": 55.99,
                "category_id": categories[3].id,  # Mugs
                "brand": "EGM",
                "sku": "MUG-001",
                "stock_quantity": 80,
                "images": []
            },
            {
                "name_en": "Professional Sauce Boats Set",
                "name_ro": "Set Sosnițe Profesionale",
                "slug": "professional-sauce-boats-set",
                "description_en": "Professional sauce boats for fine dining",
                "description_ro": "Sosnițe profesionale pentru fine dining",
                "short_description_en": "Sauce boats for fine dining",
                "short_description_ro": "Sosnițe pentru fine dining",
                "price": 75.99,
                "category_id": categories[4].id,  # Sauciers
                "brand": "EGM",
                "sku": "SAU-001",
                "stock_quantity": 25,
                "images": []
            },
            {
                "name_en": "Professional Cutlery Set",
                "name_ro": "Set Tăvițe Profesionale",
                "slug": "professional-cutlery-set",
                "description_en": "Professional knives, forks, and spoons set",
                "description_ro": "Set de cuțite, furculițe și linguri profesionale",
                "short_description_en": "Professional cutlery set",
                "short_description_ro": "Set tăvițe profesionale",
                "price": 120.99,
                "category_id": categories[5].id,  # Cutlery
                "brand": "EGM",
                "sku": "CUT-001",
                "stock_quantity": 40,
                "images": []
            },
            {
                "name_en": "Professional Cooking Pots Set",
                "name_ro": "Set Oale Profesionale pentru Gătit",
                "slug": "professional-cooking-pots-set",
                "description_en": "Professional cooking pots for commercial kitchens",
                "description_ro": "Oale profesionale pentru bucătăriile comerciale",
                "short_description_en": "Professional cooking pots",
                "short_description_ro": "Oale profesionale pentru gătit",
                "price": 199.99,
                "category_id": categories[6].id,  # Pots
                "brand": "EGM",
                "sku": "POT-001",
                "stock_quantity": 15,
                "images": []
            },
            {
                "name_en": "Professional Teapots Set",
                "name_ro": "Set Ceainice Profesionale",
                "slug": "professional-teapots-set",
                "description_en": "Professional teapots for tea service",
                "description_ro": "Ceainice profesionale pentru servirea ceaiului",
                "short_description_en": "Professional teapots for tea service",
                "short_description_ro": "Ceainice profesionale pentru ceai",
                "price": 85.99,
                "category_id": categories[7].id,  # Teapots
                "brand": "EGM",
                "sku": "TEA-001",
                "stock_quantity": 20,
                "images": []
            },
            {
                "name_en": "Professional Frying Pans Set",
                "name_ro": "Set Tigăi Profesionale",
                "slug": "professional-frying-pans-set",
                "description_en": "Professional frying pans for commercial kitchens",
                "description_ro": "Tigăi profesionale pentru bucătăriile comerciale",
                "short_description_en": "Professional frying pans",
                "short_description_ro": "Tigăi profesionale",
                "price": 159.99,
                "category_id": categories[8].id,  # Pans
                "brand": "EGM",
                "sku": "PAN-001",
                "stock_quantity": 18,
                "images": []
            },
            {
                "name_en": "Special Offer Bundle",
                "name_ro": "Pachet Ofertă Specială",
                "slug": "special-offer-bundle",
                "description_en": "Special discounted bundle of professional tableware",
                "description_ro": "Pachet redus special de veselă profesională",
                "short_description_en": "Special offer bundle",
                "short_description_ro": "Pachet ofertă specială",
                "price": 299.99,
                "category_id": categories[9].id,  # Deals
                "brand": "EGM",
                "sku": "DEAL-001",
                "stock_quantity": 10,
                "images": []
            }
        ]
        
        for prod_data in products_data:
            product = crud.create_product(db, schemas.ProductCreate(**prod_data))
            print(f"Created product: {product.name_en}")
        
        # Create admin user
        admin_user = crud.create_user(db, schemas.UserCreate(
            email="admin@egmhoreca.com",
            username="admin",
            full_name="EGM Horeca Admin",
            password="admin123",
            role="admin",
            phone="+40 123 456 789"
        ))
        print(f"Created admin user: {admin_user.username}")
        
        # Create sample customer
        customer = crud.create_user(db, schemas.UserCreate(
            email="customer@example.com",
            username="customer",
            full_name="John Doe",
            password="customer123",
            role="customer",
            phone="+40 987 654 321"
        ))
        print(f"Created customer user: {customer.username}")
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
