import 'package:flutter/material.dart';
import 'models.dart';
import 'api_service.dart';

class RestaurantMenuScreen extends StatefulWidget {
  final String restaurantId;
  final User currentUser;

  RestaurantMenuScreen({
    super.key, 
    required this.restaurantId,
    required this.currentUser,
  });

  @override
  _RestaurantMenuScreenState createState() => _RestaurantMenuScreenState();
}

class _RestaurantMenuScreenState extends State<RestaurantMenuScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<MealBundle>> _bundlesFuture;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  void _fetchData() {
    setState(() {
      _bundlesFuture = _apiService.fetchBundles(widget.currentUser.id, widget.restaurantId);
    });
  }

  bool _isDishUnsafe(Dish dish) {
    final dishSet = dish.allergens.map((e) => e.toLowerCase()).toSet();
    final userSet = widget.currentUser.allergensStrict.map((e) => e.toLowerCase()).toSet();
    return dishSet.intersection(userSet).isNotEmpty;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900], // Dark charcoal background
      appBar: AppBar(
        title: Text("Curate Recommendations", style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: FutureBuilder<List<MealBundle>>(
        future: _bundlesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator(color: Colors.white));
          } else if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                   Icon(Icons.error_outline, size: 48, color: Colors.orange),
                   SizedBox(height: 16),
                   Text("Something went wrong", style: TextStyle(color: Colors.white, fontSize: 18)),
                   Text("${snapshot.error}", style: TextStyle(color: Colors.grey), textAlign: TextAlign.center),
                   SizedBox(height: 24),
                   ElevatedButton(
                     onPressed: _fetchData,
                     style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: Colors.black),
                     child: Text("Retry"),
                   )
                ],
              ),
            );
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(
              child: Text("No recommendations found.", style: TextStyle(color: Colors.white, fontSize: 18)),
            );
          }

          final bundles = snapshot.data!;
          return PageView.builder(
            controller: PageController(viewportFraction: 0.9), // Peek next card
            itemCount: bundles.length,
            itemBuilder: (context, index) {
              return _buildBundleCard(bundles[index]);
            },
          );
        },
      ),
    );
  }

  Widget _buildBundleCard(MealBundle bundle) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 8.0, vertical: 20.0), // Spacing between cards
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: Colors.black45, blurRadius: 10, offset: Offset(0, 5))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 1. Header
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 24, 24, 16),
            child: Text(
              bundle.title,
              style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.black87),
            ),
          ),
          
          Divider(height: 1),

          // 2. Dish List
          Expanded(
            child: ListView.separated(
              padding: EdgeInsets.all(16),
              itemCount: bundle.dishes.length,
              separatorBuilder: (ctx, i) => SizedBox(height: 16),
              itemBuilder: (context, index) {
                return _buildDishItem(bundle.dishes[index]);
              },
            ),
          ),

          // 3. Explanation Section ("Why this?")
          Container(
            padding: EdgeInsets.all(20),
            color: Colors.yellow[50], // Light yellow background
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.lightbulb_outline, color: Colors.orange[800], size: 20),
                    SizedBox(width: 8),
                    Text("Why this?", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.orange[900])),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  bundle.explanation,
                  style: TextStyle(fontStyle: FontStyle.italic, color: Colors.black87),
                ),
              ],
            ),
          ),

          // 4. Footer Actions
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  "\$${bundle.totalPrice.toStringAsFixed(2)}",
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.green[800]),
                ),
                ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                  ),
                  child: Text("Order Now", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDishItem(Dish dish) {
    bool isUnsafe = _isDishUnsafe(dish);
    // Placeholder image
    final imageProvider = NetworkImage('https://images.unsplash.com/photo-1546069901-ba9599a7e63c');

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Dish Image
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            image: DecorationImage(image: imageProvider, fit: BoxFit.cover),
          ),
        ),
        SizedBox(width: 16),
        
        // Dish Details
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                dish.name,
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.black87),
              ),
              SizedBox(height: 4),
              
              // Spiciness + Tags
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: [
                  if (dish.spiceLevel > 0)
                    Text('🌶️' * dish.spiceLevel, style: TextStyle(fontSize: 12)),
                  ...dish.tags.map((tag) => Chip(
                    label: Text(tag, style: TextStyle(fontSize: 10, color: Colors.white)),
                    backgroundColor: Colors.black54,
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  )).toList()
                ],
              ),
            ],
          ),
        ),

        // Price or Warning
        isUnsafe 
          ? Icon(Icons.warning_amber_rounded, color: Colors.red, size: 32)
          : Text(
              "\$${dish.price.toStringAsFixed(0)}",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.green[700]),
            ),
      ],
    );
  }
}
