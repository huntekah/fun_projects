# ML System Design Solutions - TODO

This file tracks the implementation status of each system design solution.

## Implementation Status

### ✅ Completed Systems

1. **nearby_places_recommender** - Local place recommendation system
   - ✅ Complete implementation with requirements, design, ML models
   - ✅ Two-stage architecture (candidate generation + ranking)
   - ✅ Wide & deep model with geospatial indexing
   - ✅ Production-ready code examples

### 🚧 In Progress Systems

*None currently in progress*

### 📋 Systems To Implement

2. **restaurant_recommender** - Restaurant recommendation engine
   - 📁 Directory created
   - ❌ Requirements analysis needed
   - ❌ Design documentation needed
   - ❌ ML model implementation needed

3. **instagram_short_video_recommendation** - Short-form video recommendation system
   - 📁 Directory created  
   - ❌ Requirements analysis needed
   - ❌ Design documentation needed
   - ❌ ML model implementation needed

4. **place_deduplication_system** - Scalable batch processing for 1B+ place deduplication
   - 📁 Directory created
   - ❌ Requirements analysis needed
   - ❌ Design documentation needed
   - ❌ ML model implementation needed

5. **facebook_marketplace_recommendation** - Marketplace feed recommendations
   - 📁 Directory created
   - ❌ Requirements analysis needed
   - ❌ Design documentation needed
   - ❌ ML model implementation needed

6. **places_recommendation_system** - Large-scale place recommendations (~100M places)
   - 📁 Directory created
   - ❌ Requirements analysis needed
   - ❌ Design documentation needed
   - ❌ ML model implementation needed

7. **illegal_trading_detection** - Binary classifier for detecting illegal posts/users (weapons, etc.)
   - 📁 Directory created
   - ❌ Requirements analysis needed
   - ❌ Design documentation needed
   - ❌ ML model implementation needed

8. **gaming_video_recommendation** - Gaming content recommendation system
   - 📁 Directory created
   - ❌ Requirements analysis needed
   - ❌ Design documentation needed
   - ❌ ML model implementation needed

## Implementation Priority

### High Priority (Core recommendation systems)
1. **restaurant_recommender** - Similar to nearby places but food-specific
2. **instagram_short_video_recommendation** - Content-based + engagement modeling
3. **facebook_marketplace_recommendation** - E-commerce recommendations

### Medium Priority (Specialized systems)
4. **places_recommendation_system** - Large-scale variation of nearby places
5. **gaming_video_recommendation** - Gaming-specific content recommendations

### Lower Priority (Data processing & classification)
6. **place_deduplication_system** - Data engineering focus
7. **illegal_trading_detection** - Binary classification system

## Implementation Guidelines

For each system, follow the template structure:

### Phase 1: Requirements & Design
- [ ] requirements/functional.md
- [ ] requirements/non_functional.md  
- [ ] requirements/constraints.md
- [ ] design/high_level.md
- [ ] design/ml_pipeline.md

### Phase 2: Implementation
- [ ] implementation/ml_models.py
- [ ] implementation/data_models.py
- [ ] implementation/training_pipeline.py
- [ ] implementation/inference_pipeline.py

### Phase 3: Operations
- [ ] scaling/capacity_planning.md
- [ ] monitoring/metrics.md
- [ ] alternatives/trade_offs.md

## Next Steps

1. **Start with restaurant_recommender** - builds on nearby places concepts
2. **Focus on unique ML challenges** for each system (video recommendations, deduplication algorithms, etc.)
3. **Include production considerations** - not just academic ML models
4. **Add diagrams** when implementation is complete

## Notes

- Each system should demonstrate different ML techniques and architectural patterns
- Include real-world constraints and trade-offs in designs
- Code examples should be production-ready, not just pseudocode
- Consider different scales: 100K users vs 100M users vs 1B+ items