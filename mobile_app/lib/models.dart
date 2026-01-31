class Dish {
  final String id;
  final String name;
  final String description;
  final double price;
  final List<String> allergens;
  final List<String> tags;
  final int spiceLevel;

  Dish({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.allergens,
    required this.tags,
    required this.spiceLevel,
  });

  factory Dish.fromJson(Map<String, dynamic> json) {
    return Dish(
      id: json['id'],
      name: json['name'],
      description: json['description'] ?? '',
      price: json['price'].toDouble(),
      allergens: List<String>.from(json['allergens'] ?? []),
      tags: List<String>.from(json['tags'] ?? []),
      spiceLevel: json['spice_level'] ?? 0,
    );
  }
}

class MealBundle {
  final String title;
  final List<Dish> dishes;
  final double totalPrice;
  final String explanation;

  MealBundle({
    required this.title,
    required this.dishes,
    required this.totalPrice,
    required this.explanation,
  });

  factory MealBundle.fromJson(Map<String, dynamic> json) {
    var list = json['dishes'] as List;
    List<Dish> dishesList = list.map((i) => Dish.fromJson(i)).toList();

    return MealBundle(
      title: json['title'],
      dishes: dishesList,
      totalPrice: json['total_price'].toDouble(),
      explanation: json['explanation'],
    );
  }
}

class User {
  final String id;
  final List<String> allergensStrict;

  User({required this.id, required this.allergensStrict});
}
