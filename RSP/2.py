class Car:
    def __init__(self, car_type, passenger_capacity):
        self.car_type = car_type
        self.passenger_capacity = passenger_capacity

    def get_car_details(self):
        raise NotImplementedError("Этот метод должен быть переопределен в подклассах.")


class PassengerCar(Car):
    def __init__(self, passenger_capacity, comfort_level):
        super().__init__("Пассажирский вагон", passenger_capacity)
        self.comfort_level = comfort_level

    def get_car_details(self):
        return f"{self.car_type} - Вместимость: {self.passenger_capacity}, Уровень комфорта: {self.comfort_level}"


class BaggageCar(Car):
    def __init__(self, luggage_capacity):
        super().__init__("Багажный вагон", 0)  
        self.luggage_capacity = luggage_capacity

    def get_car_details(self):
        return f"{self.car_type} - Вместимость багажа: {self.luggage_capacity}"


class Train:
    def __init__(self):
        self.cars = []

    def add_car(self, car):
        self.cars.append(car)

    def get_total_passengers(self):
        return sum(car.passenger_capacity for car in self.cars if isinstance(car, PassengerCar))

    def sort_cars_by_comfort_level(self):
        self.cars.sort(key=lambda car: car.comfort_level if isinstance(car, PassengerCar) else float('inf'))

    def find_cars_in_passenger_range(self, min_capacity, max_capacity):
        return [car for car in self.cars if isinstance(car, PassengerCar) and min_capacity <= car.passenger_capacity <= max_capacity]

    def show_train_details(self):
        for car in self.cars:
            print(car.get_car_details())


def main():
    train = Train()

    while True:
        print("\n1. Добавить пассажирский вагон")
        print("2. Добавить багажный вагон")
        print("3. Показать информацию о поезде")
        print("4. Получить общее количество пассажиров")
        print("5. Отсортировать вагоны по уровню комфорта")
        print("6. Найти вагоны по диапазону пассажиров")
        print("0. Выход")
        choice = int(input("Выберите опцию: "))

        if choice == 1:
            passenger_capacity = int(input("Введите вместимость пассажиров: "))
            comfort_level = int(input("Введите уровень комфорта: "))
            train.add_car(PassengerCar(passenger_capacity, comfort_level))
        elif choice == 2:
            luggage_capacity = int(input("Введите вместимость багажа: "))
            train.add_car(BaggageCar(luggage_capacity))
        elif choice == 3:
            train.show_train_details()
        elif choice == 4:
            print("Общее количество пассажиров:", train.get_total_passengers())
        elif choice == 5:
            train.sort_cars_by_comfort_level()
            print("Вагоны отсортированы по уровню комфорта.")
        elif choice == 6:
            min_capacity = int(input("Введите минимальную вместимость пассажиров: "))
            max_capacity = int(input("Введите максимальную вместимость пассажиров: "))
            matching_cars = train.find_cars_in_passenger_range(min_capacity, max_capacity)
            print("Соответствующие вагоны:")
            for car in matching_cars:
                print(car.get_car_details())
        elif choice == 0:
            print("Выход...")
            break
        else:
            print("Недопустимый выбор. Пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()