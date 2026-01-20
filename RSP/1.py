class Car:
    def __init__(self, id, brand, model, year_of_manufacture, color, price, license_plate):
        self.id = id
        self.brand = brand
        self.model = model
        self.year_of_manufacture = year_of_manufacture
        self.color = color
        self.price = price
        self.license_plate = license_plate

    # Геттеры
    def get_id(self):
        return self.id

    def get_brand(self):
        return self.brand

    def get_model(self):
        return self.model

    def get_year_of_manufacture(self):
        return self.year_of_manufacture

    def get_color(self):
        return self.color

    def get_price(self):
        return self.price

    def get_license_plate(self):
        return self.license_plate

    # Сеттеры
    def set_id(self, id):
        self.id = id

    def set_brand(self, brand):
        self.brand = brand

    def set_model(self, model):
        self.model = model

    def set_year_of_manufacture(self, year):
        self.year_of_manufacture = year

    def set_color(self, color):
        self.color = color

    def set_price(self, price):
        self.price = price

    def set_license_plate(self, license_plate):
        self.license_plate = license_plate

    def __str__(self):
        return (f"Car(id={self.id}, brand='{self.brand}', model='{self.model}', "
                f"year_of_manufacture={self.year_of_manufacture}, color='{self.color}', "
                f"price={self.price}, license_plate='{self.license_plate}')")

    def __hash__(self):
        return hash((self.id, self.brand, self.model, self.year_of_manufacture, self.color, self.price, self.license_plate))

# Функции для работы с массивом объектов
def filter_cars_by_brand(cars, target_brand):
    return [car for car in cars if car.get_brand().lower() == target_brand.lower()]

def filter_cars_by_model_and_year(cars, target_model, years_in_operation):
    return [car for car in cars if car.get_model().lower() == target_model.lower() and (2023 - car.get_year_of_manufacture() > years_in_operation)]

def filter_cars_by_year_and_price(cars, target_year, target_price):
    return [car for car in cars if car.get_year_of_manufacture() == target_year and car.get_price() > target_price]

# Пример использования
if __name__ == "__main__":
    car_list = [
        Car(1, "Toyota", "Corolla", 2015, "Black", 15000, "A123BC"),
        Car(2, "Honda", "Civic", 2017, "Red", 18000, "C456BB"),
        Car(3, "Ford", "Focus", 2010, "Blue", 8000, "M789EM"),
        Car(4, "Toyota", "Camry", 2018, "White", 22000, "E234EE"),
        Car(5, "BMW", "X5", 2019, "Black", 60000, "M567MM"),
    ]

    # a) Список автомобилей заданной марки
    target_brand = "Toyota"
    print(f"Список автомобилей марки {target_brand}:")
    for car in filter_cars_by_brand(car_list, target_brand):
        print(car)

    # b) Список автомобилей заданной модели, которые эксплуатируются больше лет
    target_model = "Civic"
    years_in_operation = 3
    print(f"\nСписок автомобилей модели {target_model} с эксплуатацией больше {years_in_operation} лет:")
    for car in filter_cars_by_model_and_year(car_list, target_model, years_in_operation):
        print(car)

    # c) Список автомобилей заданного года выпуска, цена которых больше указанной
    target_year = 2019
    target_price = 15000
    print(f"\nСписок автомобилей года выпуска {target_year}, цена которых больше {target_price}:")
    for car in filter_cars_by_year_and_price(car_list, target_year, target_price):
        print(car)