@page task2_page Task 2. Lazy streaming data pipeline
@section task2_implementation Implementation
* The implementation is located in the @ref project/task2 "project/task2" directory:
* - @ref project/task2/generators.py - Input data generators (range_generator, sequence_generator, repeat_generator, custom_generator)
* - @ref project/task2/operations.py - Stream operations and pipeline (pipeline, map_op, filter_op, compress_op, take_op, drop_op, take_while_op, drop_while_op, reduce_op, zip_op)
* - @ref project/task2/aggregators.py - Aggregators (to_list, to_set, to_dict, count, sum_all, product_all, min_value, max_value, first, last)

# Задача 2. Генераторы

* **Дедлайн**: 10.10.2025, 23:59
* Полный балл: 10

## Задача

- [ ] Реализовать систему для ленивой потоковой обработки данных с использованием генераторов.
Система должна включать следующие компоненты.
  - [ ] Генератор для генерации входных данных
  - [ ] Функция конвейер, последовательно применяющая переданные операции к входной последовательности
  - [ ] Поддержка встроенных функций, таких как `map`, `filter`, `zip`, `reduce` и т.д.
  - [ ] Поддержка пользовательских функций
  - [ ] Функция агрегатор, собирающая результат конвейера в коллекцию
- [ ] Добавить тесты покрывающие реализованную функциональность. Тесты должны использовать либо декоратор `pytest.fixture`, либо `pytest.mark.parametrize`.
