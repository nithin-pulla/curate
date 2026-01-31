import 'package:flutter/material.dart';
import 'dart:convert';
import '../restaurant_menu_screen.dart';
import '../models.dart';

class OnboardingScreen extends StatefulWidget {
  @override
  _OnboardingScreenState createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentStep = 0;
  final int _totalSteps = 6;

  // Answers
  String? _q1SweetSavory;
  String? _q2Texture;
  String? _q3Vibe;
  double _q4Spice = 1.0;
  final Set<String> _q5DietaryLines = {}; // "None" handled logic
  final TextEditingController _q6ChildhoodMeal = TextEditingController();

  final List<String> _dietaryOptions = ["Gluten-Free", "Vegetarian", "Peanuts", "Shellfish", "None"];

  @override
  void dispose() {
    _pageController.dispose();
    _q6ChildhoodMeal.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentStep < _totalSteps - 1) {
      _pageController.nextPage(duration: Duration(milliseconds: 300), curve: Curves.easeInOut);
      setState(() {
        _currentStep++;
      });
    } else {
      _finish();
    }
  }

  bool _isCurrentStepValid() {
    switch (_currentStep) {
      case 0: return _q1SweetSavory != null;
      case 1: return _q2Texture != null;
      case 2: return _q3Vibe != null;
      case 3: return true; // Slider always valid
      case 4: return _q5DietaryLines.isNotEmpty;
      case 5: return _q6ChildhoodMeal.text.trim().isNotEmpty;
      default: return false;
    }
  }

  void _finish() {
    // Map answers
    final answers = {
      "preference_sweet_savory": _q1SweetSavory,
      "preference_texture": _q2Texture,
      "preference_vibe": _q3Vibe,
      "spice_tolerance": _q4Spice.round(),
      "dietary_red_lines": _q5DietaryLines.toList(),
      "childhood_meal": _q6ChildhoodMeal.text.trim()
    };

    print("--- USER PERSONA JSON ---");
    print(jsonEncode(answers));

    // Extract allergens for the User model (Safety)
    // We map the "Red Lines" directly if they match strict allergens + generic constraints
    List<String> allergensForModel = [];
    if (_q5DietaryLines.contains("Peanuts")) allergensForModel.add("peanuts");
    if (_q5DietaryLines.contains("Shellfish")) allergensForModel.add("shellfish");
    // "Gluten-Free" and "Vegetarian" are constraints, not strictly "Allergens" for the *safety* list 
    // unless we map them. For now, we just pass the ID and strict allergens.
    
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => RestaurantMenuScreen(
          restaurantId: '67d606f7-509b-40c1-a91c-b18e5d3ee830',
          currentUser: User(
            id: 'c69791d1-e683-48e2-b9e5-82c42b452347',
            allergensStrict: allergensForModel,
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900], // Dark background
      appBar: AppBar(
        title: Text("Let's profile your palate.", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
        child: Column(
          children: [
             // Progress Bar
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: (_currentStep + 1) / _totalSteps,
                backgroundColor: Colors.grey[800],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.green),
                minHeight: 6,
              ),
            ),
            SizedBox(height: 32),

            // Wizard Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: NeverScrollableScrollPhysics(),
                children: [
                  _buildBinaryStep("If you could only keep one, would you choose?", "Sweet", "Savory", _q1SweetSavory, (val) => setState(() => _q1SweetSavory = val)),
                  _buildBinaryStep("Texture preference?", "Crunchy", "Creamy/Soft", _q2Texture, (val) => setState(() => _q2Texture = val)),
                  _buildBinaryStep("Tonight's vibe?", "Rich & Heavy (Pasta)", "Light & Fresh (Salads)", _q3Vibe, (val) => setState(() => _q3Vibe = val)),
                  _buildSliderStep(),
                  _buildMultiSelectStep(),
                  _buildTextStep(),
                ],
              ),
            ),
            
            // Next Button
            SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _isCurrentStepValid() ? _nextPage : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  disabledBackgroundColor: Colors.grey[800],
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 4,
                ),
                child: Text(
                  _currentStep == _totalSteps - 1 ? "Finish" : "Next", 
                  style: TextStyle(
                    fontSize: 18, 
                    fontWeight: FontWeight.bold,
                    color: _isCurrentStepValid() ? Colors.white : Colors.grey[600]
                  )
                ),
              ),
            ),
            SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  // --- Reusable Logic Steps ---

  Widget _buildBinaryStep(String question, String optionA, String optionB, String? currentValue, Function(String) onSelect) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(question, 
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
          textAlign: TextAlign.center,
        ),
        SizedBox(height: 48),
        _buildSelectionButton(optionA, currentValue == optionA, () => onSelect(optionA)),
        SizedBox(height: 16),
        _buildSelectionButton(optionB, currentValue == optionB, () => onSelect(optionB)),
      ],
    );
  }

  Widget _buildSliderStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text("Spice Tolerance (1-10)?", 
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
          textAlign: TextAlign.center,
        ),
         SizedBox(height: 16),
        Text("${_q4Spice.round()}", style: TextStyle(fontSize: 48, color: Colors.green, fontWeight: FontWeight.bold)),
        SizedBox(height: 32),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: Colors.green,
            thumbColor: Colors.white,
            inactiveTrackColor: Colors.grey[800],
            overlayColor: Colors.green.withOpacity(0.2),
            trackHeight: 12.0,
            thumbShape: RoundSliderThumbShape(enabledThumbRadius: 16.0),
          ),
          child: Slider(
            value: _q4Spice,
            min: 1,
            max: 10,
            divisions: 9,
            onChanged: (val) => setState(() => _q4Spice = val),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text("Mild", style: TextStyle(color: Colors.grey)),
              Text("Extreme", style: TextStyle(color: Colors.grey)),
            ],
          ),
        )
      ],
    );
  }

  Widget _buildMultiSelectStep() {
     return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text("Any dietary red lines?", 
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
          textAlign: TextAlign.center,
        ),
        SizedBox(height: 32),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          alignment: WrapAlignment.center,
          children: _dietaryOptions.map((option) {
            bool isSelected = _q5DietaryLines.contains(option);
            return GestureDetector(
              onTap: () {
                setState(() {
                  if (option == "None") {
                    _q5DietaryLines.clear();
                    if (!isSelected) _q5DietaryLines.add("None"); // Toggle on
                  } else {
                    _q5DietaryLines.remove("None");
                    if (isSelected) {
                      _q5DietaryLines.remove(option);
                    } else {
                      _q5DietaryLines.add(option);
                    }
                  }
                });
              },
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected ? Colors.green : Colors.transparent,
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: isSelected ? Colors.green : Colors.grey[600]!, width: 2),
                ),
                child: Text(
                  option,
                  style: TextStyle(
                    color: isSelected ? Colors.black : Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildTextStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text("What is a childhood meal that feels like a 'warm hug'?", 
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
          textAlign: TextAlign.center,
        ),
        SizedBox(height: 32),
        TextField(
          controller: _q6ChildhoodMeal,
          style: TextStyle(color: Colors.white, fontSize: 18),
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.grey[800],
            hintText: "e.g. Grandma's Chicken Soup",
            hintStyle: TextStyle(color: Colors.grey[500]),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
            contentPadding: EdgeInsets.all(24),
          ),
          maxLines: 2,
          onChanged: (_) => setState(() {}), // updates validation
        ),
      ],
    );
  }

  // --- Helper Widgets ---

  Widget _buildSelectionButton(String text, bool isSelected, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.symmetric(vertical: 24),
        decoration: BoxDecoration(
          color: isSelected ? Colors.green : Colors.grey[800],
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: isSelected ? Colors.green : Colors.transparent, width: 2),
        ),
        child: Text(
          text,
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            // FIXED: Black text on Green (Selected), White on Grey (Unselected)
            color: isSelected ? Colors.black : Colors.white,
          ),
        ),
      ),
    );
  }
}
