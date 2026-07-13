# -*- coding: utf-8 -*-

"""
Offline Database for CropSense AI
Contains comprehensive offline solutions for all 38 PlantVillage classes.
"""

# Default template for healthy plants to avoid duplication
def get_healthy_data(plant_name, scientific_name):
    return {
        "plant_name": plant_name,
        "plant_scientific": scientific_name,
        "disease_name": "Healthy",
        "disease_pathogen": "None (Healthy Plant)",
        "is_healthy": True,
        "severity": "Excellent",
        "confidence_note": "Plant leaves appear healthy and vigorous.",
        "symptoms": "No visible symptoms. Healthy green foliage with good turgidity.",
        "description": f"The {plant_name} plant shows no signs of active disease or pest infestation. Chlorophyll levels and leaf structure are normal.",
        "treatment": "No active disease treatment required. Continue standard cultural management practices.",
        "prevention": "Ensure proper irrigation, crop rotation, and avoid overhead watering to prevent future fungal outbreaks.",
        "medicine": {
            "name": "None Required",
            "type": "N/A",
            "active_ingredient": "N/A",
            "dose": "N/A",
            "frequency": "N/A",
            "method": "N/A",
            "preharvest_interval": "N/A",
            "safety": "N/A",
            "alternatives": [],
            "caution": "Do not apply chemical pesticides to healthy plants."
        },
        "fertilizer": {
            "name": "Balanced Maintenance Fertilizer",
            "type": "Organic / Bio",
            "npk_n": "10",
            "npk_p": "10",
            "npk_k": "10",
            "dose": "Standard maintenance rate",
            "timing": "Regular growing season intervals",
            "method": "Soil application",
            "benefits": "Maintains soil nutrient balance and supports healthy development.",
            "additional_supplement": "Micronutrient mix (Iron, Magnesium)",
            "tips": ["Monitor soil moisture levels regularly.", "Apply organic compost to maintain soil biology."]
        },
        "cnn_agreement": True,
        "cnn_note": "CNN correctly identified the plant leaf as healthy."
    }

OFFLINE_DB = {
    # ═══════════════════════════════════════════════════
    # HEALTHY CLASSES
    # ═══════════════════════════════════════════════════
    "Apple___healthy": get_healthy_data("Apple", "Malus domestica"),
    "Blueberry___healthy": get_healthy_data("Blueberry", "Vaccinium corymbosum"),
    "Cherry_(including_sour)___healthy": get_healthy_data("Cherry", "Prunus cerasus"),
    "Corn_(maize)___healthy": get_healthy_data("Corn (Maize)", "Zea mays"),
    "Grape___healthy": get_healthy_data("Grape", "Vitis vinifera"),
    "Peach___healthy": get_healthy_data("Peach", "Prunus persica"),
    "Pepper,_bell___healthy": get_healthy_data("Pepper (Bell)", "Capsicum annuum"),
    "Potato___healthy": get_healthy_data("Potato", "Solanum tuberosum"),
    "Raspberry___healthy": get_healthy_data("Raspberry", "Rubus idaeus"),
    "Soybean___healthy": get_healthy_data("Soybean", "Glycine max"),
    "Strawberry___healthy": get_healthy_data("Strawberry", "Fragaria × ananassa"),
    "Tomato___healthy": get_healthy_data("Tomato", "Solanum lycopersicum"),

    # ═══════════════════════════════════════════════════
    # APPLE DISEASES
    # ═══════════════════════════════════════════════════
    "Apple___Apple_scab": {
        "plant_name": "Apple",
        "plant_scientific": "Malus domestica",
        "disease_name": "Apple Scab",
        "disease_pathogen": "Venturia inaequalis (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Classified based on diagnostic foliar scab lesions.",
        "symptoms": "Olive-green to velvety dark spots on leaves and fruit. Leaves may curl, turn yellow, and drop prematurely.",
        "description": "Apple scab is a major fungal disease that overwinters on fallen leaves. It infects young foliage during wet spring conditions, leading to cosmetic damage on fruit and tree defoliation.",
        "treatment": "Prune infected twigs. Apply sulfur or copper-based fungicides during green tip and petal fall stages.",
        "prevention": "Rake and destroy fallen leaves in autumn. Plant resistant varieties like Liberty or Jonafree.",
        "medicine": {
            "name": "Myclobutanil or Copper Fungicide",
            "type": "Systemic / Contact",
            "active_ingredient": "Myclobutanil (0.05%) or Liquid Copper octanoate",
            "dose": "2.5 ml per litre of water",
            "frequency": "Every 10-14 days starting at bud break",
            "method": "Foliar Spray",
            "preharvest_interval": "14 days",
            "safety": "Wear protective gloves and mask. Do not spray during windy conditions.",
            "alternatives": ["Wettable Sulfur", "Neem Oil"],
            "caution": "Do not apply copper fungicides during hot weather to avoid leaf phytotoxicity."
        },
        "fertilizer": {
            "name": "Low-Nitrogen / High-Potassium Fertilizer",
            "type": "Chemical",
            "npk_n": "5",
            "npk_p": "10",
            "npk_k": "15",
            "dose": "500g per mature tree",
            "timing": "Late spring",
            "method": "Soil application around drip line",
            "benefits": "Strengthens cell walls and improves disease resistance.",
            "additional_supplement": "Calcium chloride spray (for fruit quality)",
            "tips": ["Avoid excessive nitrogen which causes soft, susceptible vegetative growth."]
        },
        "cnn_agreement": True,
        "cnn_note": "Foliar lesions align with typical Apple Scab manifestations."
    },

    "Apple___Black_rot": {
        "plant_name": "Apple",
        "plant_scientific": "Malus domestica",
        "disease_name": "Black Rot",
        "disease_pathogen": "Botryosphaeria obtusa (Fungus)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Identified by frog-eye leaf spot pattern.",
        "symptoms": "Frog-eye spots on leaves (purple margin with tan center), cankers on limbs, and black decaying rings on fruit.",
        "description": "Black Rot is a fungal disease that can infect leaves, twigs, and fruit. It overwinters in dead wood and mummified fruit, spreading rapidly during warm, wet summer periods.",
        "treatment": "Prune out dead wood, cankers, and remove mummified fruit. Apply protective fungicides.",
        "prevention": "Prune trees annually to keep the canopy open. Remove infected branches from the orchard.",
        "medicine": {
            "name": "Captan or Flutriafol",
            "type": "Contact / Systemic",
            "active_ingredient": "Captan (50% WP) or Flutriafol",
            "dose": "2g per litre of water",
            "frequency": "Every 7-10 days from pink bud to cover sprays",
            "method": "Foliar Spray",
            "preharvest_interval": "7 days",
            "safety": "Keep away from skin and eyes. Wear protective eyewear.",
            "alternatives": ["Copper octanoate", "Lime sulfur"],
            "caution": "Avoid direct application when bees are actively foraging."
        },
        "fertilizer": {
            "name": "Organic Compost & Kelp Meal",
            "type": "Organic",
            "npk_n": "2",
            "npk_p": "2",
            "npk_k": "4",
            "dose": "2-3 kg per tree base",
            "timing": "Early spring",
            "method": "Mulching and soil incorporation",
            "benefits": "Improves soil health and builds tree vitality to recover from wood cankers.",
            "additional_supplement": "Foliar trace mineral spray",
            "tips": ["Keep mulch away from the direct tree trunk base to prevent moisture rot."]
        },
        "cnn_agreement": True,
        "cnn_note": "Leaf spot indicators are highly characteristic of Black Rot."
    },

    "Apple___Cedar_apple_rust": {
        "plant_name": "Apple",
        "plant_scientific": "Malus domestica",
        "disease_name": "Cedar Apple Rust",
        "disease_pathogen": "Gymnosporangium juniperi-virginianae (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Bright orange spots provide high diagnostic confidence.",
        "symptoms": "Bright orange-yellow spots on upper leaf surfaces. Spore cups (aecia) appear on under-leaf surfaces later in summer.",
        "description": "This rust fungus requires two hosts to complete its life cycle: Eastern Red Cedar and Apple. In spring, gelatinous galls on cedars release spores that infect nearby apple leaves.",
        "treatment": "Apply immunizing fungicides at the first sign of orange spots or during apple bud break.",
        "prevention": "Remove nearby wild cedars if possible. Plant rust-resistant cultivars.",
        "medicine": {
            "name": "Myclobutanil or Triadimefon",
            "type": "Systemic Fungicide",
            "active_ingredient": "Myclobutanil",
            "dose": "2 ml per litre of water",
            "frequency": "Apply at bud break, repeat 3 times at 10-day intervals",
            "method": "Foliar Spray",
            "preharvest_interval": "14 days",
            "safety": "Avoid breathing spray mist. Use personal protection equipment.",
            "alternatives": ["Sulfur dusts", "Serenade Opti (Biological)"],
            "caution": "Timing is critical. Spraying after lesions turn dry and brown is ineffective."
        },
        "fertilizer": {
            "name": "Potassium-Rich Fertilizer",
            "type": "Chemical",
            "npk_n": "8",
            "npk_p": "8",
            "npk_k": "24",
            "dose": "300g per tree",
            "timing": "Post-bloom stage",
            "method": "Broadcasting under canopy",
            "benefits": "Helps tree withstand stress and foliar damage from rust.",
            "additional_supplement": "Humic acid",
            "tips": ["Adequate potassium helps maintain leaf moisture and stomatal function."]
        },
        "cnn_agreement": True,
        "cnn_note": "Orange rust spot characteristics align with Cedar Apple Rust."
    },

    # ═══════════════════════════════════════════════════
    # CHERRY DISEASES
    # ═══════════════════════════════════════════════════
    "Cherry_(including_sour)___Powdery_mildew": {
        "plant_name": "Cherry",
        "plant_scientific": "Prunus cerasus",
        "disease_name": "Powdery Mildew",
        "disease_pathogen": "Podosphaera clandestina (Fungus)",
        "is_healthy": False,
        "severity": "Mild",
        "confidence_note": "Identified by white powdery coating on leaves.",
        "symptoms": "White, powdery patches of fungal growth on leaves and shoots. Leaves may warp, curl upward, and stunt.",
        "description": "Powdery mildew affects sweet and sour cherries, attacking young leaves and fruit. It thrives in high humidity and warm, dry daytime temperatures.",
        "treatment": "Apply sulfur or potassium bicarbonate sprays. Prune to improve canopy sunlight exposure.",
        "prevention": "Ensure good spacing between trees. Avoid shady orchard locations.",
        "medicine": {
            "name": "Tebuconazole or Potassium Bicarbonate",
            "type": "Systemic / Contact",
            "active_ingredient": "Tebuconazole (0.02%) or Potassium Bicarbonate",
            "dose": "3g per litre (Bicarbonate) or 1.5 ml per litre (Tebuconazole)",
            "frequency": "Every 7-14 days starting at petal fall",
            "method": "Foliar Spray",
            "preharvest_interval": "0 days (Bicarbonate), 14 days (Tebuconazole)",
            "safety": "Bicarbonate is non-toxic. Wear gloves for chemical fungicides.",
            "alternatives": ["Neem Oil", "Horticultural oil"],
            "caution": "Do not apply oils within 2 weeks of a sulfur treatment to avoid leaf burn."
        },
        "fertilizer": {
            "name": "Compost Tea and Balanced Bio-Fertilizer",
            "type": "Organic",
            "npk_n": "4",
            "npk_p": "4",
            "npk_k": "4",
            "dose": "5 litres of diluted compost tea per tree base",
            "timing": "Monthly during spring and summer",
            "method": "Drenching",
            "benefits": "Enhances beneficial foliar microbial populations to fight fungi.",
            "additional_supplement": "Silicon-based supplements",
            "tips": ["Silicon helps strengthen leaf epidermal cells against fungal penetration."]
        },
        "cnn_agreement": True,
        "cnn_note": "Foliar warping and powdery coating match Powdery Mildew symptoms."
    },

    # ═══════════════════════════════════════════════════
    # CORN DISEASES
    # ═══════════════════════════════════════════════════
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "plant_name": "Corn",
        "plant_scientific": "Zea mays",
        "disease_name": "Gray Leaf Spot",
        "disease_pathogen": "Cercospora zeae-maydis (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Rectangular, vein-limited lesions identified.",
        "symptoms": "Rectangular, tan to gray lesions running parallel to leaf veins. Lesions look like blocky stripes.",
        "description": "Gray Leaf Spot is a highly damaging fungal disease that thrives in humid, warm conditions. It blocks photosynthesis, leading to significant stalk lodging and yield loss.",
        "treatment": "Apply strobilurin or triazole fungicides if lesions appear near the ear leaf around silking stage.",
        "prevention": "Rotate crops with non-grasses. Till crop residue in the autumn. Plant tolerant hybrids.",
        "medicine": {
            "name": "Pyraclostrobin or Azoxystrobin",
            "type": "Systemic Fungicide",
            "active_ingredient": "Pyraclostrobin (23.6%)",
            "dose": "1.2 ml per litre of water",
            "frequency": "Single application at VT (tasseling) stage if pressure is high",
            "method": "Foliar Spray (Boom Sprayer)",
            "preharvest_interval": "30 days",
            "safety": "Follow strict agricultural chemical safety guidelines. Use respirator.",
            "alternatives": ["Propiconazole", "Bacillus subtilis (Biological)"],
            "caution": "Do not apply under hot, dry conditions to avoid crop injury."
        },
        "fertilizer": {
            "name": "High-Nitrogen & Zinc Fertilizer",
            "type": "Chemical",
            "npk_n": "20",
            "npk_p": "10",
            "npk_k": "10",
            "dose": "150-200 kg per hectare (split application)",
            "timing": "Side-dressed before tasseling",
            "method": "Band application",
            "benefits": "Supports rapid growth and improves stress recovery.",
            "additional_supplement": "Zinc sulfate (micronutrient)",
            "tips": ["Ensure potassium levels are sufficient to maintain stalk strength."]
        },
        "cnn_agreement": True,
        "cnn_note": "Vein-bound rectangular spots are diagnostic for Gray Leaf Spot."
    },

    "Corn_(maize)___Common_rust_": {
        "plant_name": "Corn",
        "plant_scientific": "Zea mays",
        "disease_name": "Common Rust",
        "disease_pathogen": "Puccinia sorghi (Fungus)",
        "is_healthy": False,
        "severity": "Mild",
        "confidence_note": "Distinct powdery reddish-brown pustules found.",
        "symptoms": "Reddish-brown, powdery pustules on both upper and lower surfaces of leaves. Pustules turn black late in the season.",
        "description": "Common rust is caused by a fungus that spreads via windblown spores from southern overwintering regions. It thrives in cool, moist, and humid weather.",
        "treatment": "Usually not required as plants recover, but fungicides can be used on valuable seed corn or in severe outbreaks.",
        "prevention": "Use rust-resistant corn hybrids. Plant early in the season.",
        "medicine": {
            "name": "Propiconazole or Pyraclostrobin",
            "type": "Systemic Fungicide",
            "active_ingredient": "Propiconazole (41.8%)",
            "dose": "1 ml per litre of water",
            "frequency": "One application at first sign of pustules",
            "method": "Foliar Spray",
            "preharvest_interval": "30 days",
            "safety": "Keep away from skin. Wear goggles and long sleeves.",
            "alternatives": ["Copper octanoate", "Organic sulfur dust"],
            "caution": "Typically not economical to spray field corn unless infection occurs before tasseling."
        },
        "fertilizer": {
            "name": "Balanced Starter and Side-dress Fertilizer",
            "type": "Chemical",
            "npk_n": "15",
            "npk_p": "15",
            "npk_k": "15",
            "dose": "100 kg per hectare",
            "timing": "At planting and 4 weeks post-emergence",
            "method": "Broadcast / Band",
            "benefits": "Promotes steady vegetative vigor to withstand early rust attacks.",
            "additional_supplement": "Magnesium / Sulfur mix",
            "tips": ["Healthy nutrient levels enable the crop to tolerate foliar rust without severe yield loss."]
        },
        "cnn_agreement": True,
        "cnn_note": "Pustule color and shape are highly indicative of Common Rust."
    },

    "Corn_(maize)___Northern_Leaf_Blight": {
        "plant_name": "Corn",
        "plant_scientific": "Zea mays",
        "disease_name": "Northern Corn Leaf Blight",
        "disease_pathogen": "Exserohilum turcicum (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Cigar-shaped tan lesions indicate Northern Corn Leaf Blight.",
        "symptoms": "Long, elliptical, cigar-shaped grayish-green to tan lesions on leaves. Lesions can grow up to 6 inches long.",
        "description": "Northern Corn Leaf Blight (NCLB) is a destructive fungal disease that spreads during cool, wet, and humid conditions. It destroys leaf tissue and results in high yield loss if it strikes the ear leaf early.",
        "treatment": "Apply triazole or strobilurin fungicides if symptoms appear prior to silking.",
        "prevention": "Rotate crops to reduce residue inoculum. Use NCLB-resistant hybrids. Till under infected residue.",
        "medicine": {
            "name": "Tebuconazole + Trifloxystrobin",
            "type": "Systemic Fungicide Mix",
            "active_ingredient": "Tebuconazole + Trifloxystrobin",
            "dose": "1.5 ml per litre of water",
            "frequency": "Apply once at tasseling (VT) if spots are visible below the ear",
            "method": "Foliar Spray",
            "preharvest_interval": "36 days",
            "safety": "Handle chemical with care. Wear chemical-resistant gloves.",
            "alternatives": ["Azoxystrobin", "Copper Fungicides"],
            "caution": "Applying fungicides after significant leaf drying has occurred will not restore yield."
        },
        "fertilizer": {
            "name": "Nitrogen and Potassium Side-dress",
            "type": "Chemical",
            "npk_n": "24",
            "npk_p": "0",
            "npk_k": "12",
            "dose": "150 kg per hectare",
            "timing": "V6 to V8 growth stage",
            "method": "Inject or side-dress band",
            "benefits": "Compensates for lost leaf photosynthetic area by boosting green tissue growth.",
            "additional_supplement": "Manganese sulfate spray",
            "tips": ["Maintain high potassium to reinforce cell structure and stalk integrity against lodging."]
        },
        "cnn_agreement": True,
        "cnn_note": "Elliptical, cigar-shaped spots are typical of Northern Corn Leaf Blight."
    },

    # ═══════════════════════════════════════════════════
    # GRAPE DISEASES
    # ═══════════════════════════════════════════════════
    "Grape___Black_rot": {
        "plant_name": "Grape",
        "plant_scientific": "Vitis vinifera",
        "disease_name": "Black Rot",
        "disease_pathogen": "Guignardia bidwellii (Fungus)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Tan leaf spots and shriveled fruit clusters indicate Black Rot.",
        "symptoms": "Small, circular tan spots on leaves with dark borders. Shriveled, dry, black mummy berries in clusters.",
        "description": "Black Rot is one of the most serious diseases of grapes. It infects leaves, shoots, and berries during warm, humid spring periods, turning grapes into useless, hard black mummies.",
        "treatment": "Remove and destroy mummy grapes. Spray fungicides from bud break through post-bloom.",
        "prevention": "Prune out old wood and debris. Plant in full sun with excellent air circulation. Keep vines off the ground.",
        "medicine": {
            "name": "Mancozeb or Myclobutanil",
            "type": "Contact / Systemic",
            "active_ingredient": "Mancozeb (75% DF) or Myclobutanil",
            "dose": "2g per litre (Mancozeb) or 2 ml per litre (Myclobutanil)",
            "frequency": "Every 10-14 days starting at 1-inch shoot growth",
            "method": "Foliar Spray",
            "preharvest_interval": "66 days (Mancozeb), 14 days (Myclobutanil)",
            "safety": "Observe pre-harvest limits strictly. Wear protective suit.",
            "alternatives": ["Copper sulfate", "Captan"],
            "caution": "Mancozeb has a very long pre-harvest interval; do not apply late in the season."
        },
        "fertilizer": {
            "name": "Low-Nitrogen / Organic Compost Mix",
            "type": "Organic",
            "npk_n": "3",
            "npk_p": "4",
            "npk_k": "6",
            "dose": "1-2 kg per vine",
            "timing": "Early spring",
            "method": "Spread around root zone",
            "benefits": "Supports vine health without causing excessive dense leaf growth.",
            "additional_supplement": "Boron (foliar micro-spray if deficient)",
            "tips": ["Excessive nitrogen causes dense leaf canopies, trapping humidity and promoting black rot."]
        },
        "cnn_agreement": True,
        "cnn_note": "Foliar spots are consistent with Grape Black Rot symptoms."
    },

    "Grape___Esca_(Black_Measles)": {
        "plant_name": "Grape",
        "plant_scientific": "Vitis vinifera",
        "disease_name": "Esca (Black Measles)",
        "disease_pathogen": "Phaeomoniella chlamydospora & Phaeoacremonium aleophilum (Fungi)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Tigar-stripe leaf discoloration is a distinct Esca symptom.",
        "symptoms": "'Tiger-stripe' chlorosis on leaves (yellow/red strips between veins with green borders). Dark spots on berry skin.",
        "description": "Esca is a complex wood-rotting disease affecting older vineyards. Fungi enter through pruning wounds, slowly killing vine wood and releasing toxins that disfigure leaves and fruits.",
        "treatment": "No chemical treatment cures Esca once in the wood. Prune out dead trunks, protect pruning wounds with paste.",
        "prevention": "Disinfect pruning tools between vines. Apply wound sealants immediately after pruning.",
        "medicine": {
            "name": "Wound Sealant Paste or Trichoderma biocontrols",
            "type": "Protectant / Bio-fungicide",
            "active_ingredient": "Tebuconazole wound paste or Trichoderma harzianum spores",
            "dose": "Apply directly to fresh cuts (paste)",
            "frequency": "Apply to every pruning wound in winter",
            "method": "Painting wounds with brush or spray",
            "preharvest_interval": "N/A",
            "safety": "Wear gloves when handling paints and sealants.",
            "alternatives": ["Copper paste", "Liquid pruning sealers"],
            "caution": "Pruning wound protection must be applied on the same day as pruning to prevent fungal entry."
        },
        "fertilizer": {
            "name": "Humic Acid and Micronutrient Blend",
            "type": "Organic",
            "npk_n": "5",
            "npk_p": "5",
            "npk_k": "10",
            "dose": "250g per vine",
            "timing": "Post-harvest / Late autumn",
            "method": "Soil application",
            "benefits": "Re-vitalizes damaged root and vascular systems in older vines.",
            "additional_supplement": "Zinc / Manganese spray",
            "tips": ["Avoid heavy crop loads on Esca-compromised vines to prevent sudden vine collapse (apoplexy)."]
        },
        "cnn_agreement": True,
        "cnn_note": "Tiger-stripe leaf necrosis pattern matches Esca description."
    },

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "plant_name": "Grape",
        "plant_scientific": "Vitis vinifera",
        "disease_name": "Isariopsis Leaf Spot (Leaf Blight)",
        "disease_pathogen": "Pseudocercospora vitis (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Irregular necrotic leaf spots observed.",
        "symptoms": "Dull brown, irregular spots on leaves, starting from lower foliage. Leaves dry out, wither, and fall.",
        "description": "Isariopsis leaf spot typically strikes grapes later in the summer. While less destructive than Black Rot, severe outbreaks can cause early defoliation, weakening the vine for winter.",
        "treatment": "Apply copper or standard protective fungicides during summer.",
        "prevention": "Prune lower leaves to improve airflow and keep foliage dry. Rake up old leaf debris.",
        "medicine": {
            "name": "Copper Hydroxide or Pyraclostrobin",
            "type": "Contact Fungicide / Systemic",
            "active_ingredient": "Copper Hydroxide (53.8%)",
            "dose": "2g per litre of water",
            "frequency": "Every 14 days during warm, humid late summer months",
            "method": "Foliar Spray",
            "preharvest_interval": "1 day (Copper)",
            "safety": "Use protective eyewear to avoid copper dust contact.",
            "alternatives": ["Neem Oil", "Azoxystrobin"],
            "caution": "Do not apply copper within 2 weeks of oil applications to prevent phytotoxicity."
        },
        "fertilizer": {
            "name": "High-Potassium / Seaweed Extract Fertilizer",
            "type": "Organic",
            "npk_n": "2",
            "npk_p": "1",
            "npk_k": "8",
            "dose": "20 ml per litre of water",
            "frequency": "Foliar spray every 3 weeks during summer",
            "method": "Foliar Spray",
            "benefits": "Enhances late-season leaf vigor and boosts sugar accumulation in berries.",
            "additional_supplement": "Magnesium sulfate (Epsom salts)",
            "tips": ["Magnesium supports chlorophyll density and improves photosynthesis in mature grape leaves."]
        },
        "cnn_agreement": True,
        "cnn_note": "Necrotic leaf blotches match late-season Isariopsis Leaf Spot."
    },

    # ═══════════════════════════════════════════════════
    # ORANGE DISEASES
    # ═══════════════════════════════════════════════════
    "Orange___Haunglongbing_(Citrus_greening)": {
        "plant_name": "Orange",
        "plant_scientific": "Citrus sinensis",
        "disease_name": "Citrus Greening (Huanglongbing)",
        "disease_pathogen": "Candidatus Liberibacter asiaticus (Bacteria)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Mottled yellow-green leaf patterns indicate HLB.",
        "symptoms": "Asymmetrical blotchy yellow mottling on leaves, yellowing of shoots, small misshapen bitter green fruit.",
        "description": "Huanglongbing (HLB) is the most destructive citrus disease globally. It is spread by the Asian Citrus Psyllid insect. The bacteria infect the vascular system, starving the tree and leading to death in 3-5 years.",
        "treatment": "No cure exists. Remove infected trees immediately. Control the psyllid insect vector.",
        "prevention": "Use certified disease-free nursery stock. Monitor for psyllids. Spray vector controls.",
        "medicine": {
            "name": "Imidacloprid or Horticultural Oil (for Psyllid vector control)",
            "type": "Systemic Insecticide",
            "active_ingredient": "Imidacloprid (0.1%)",
            "dose": "3-5 ml per litre of water applied to root zone",
            "frequency": "Once or twice a year depending on psyllid presence",
            "method": "Soil Drench around base",
            "preharvest_interval": "14-30 days",
            "safety": "Highly toxic to bees. Do not apply when weeds or flowers are in bloom.",
            "alternatives": ["Pyrethrin spray", "Neem oil foliar spray"],
            "caution": "Removing infected trees is mandatory in commercial zones to prevent regional spread."
        },
        "fertilizer": {
            "name": "Chelated Micronutrient Fertilizer & Root Enhancer",
            "type": "Chemical / Mineral",
            "npk_n": "12",
            "npk_p": "6",
            "npk_k": "12",
            "dose": "400g per tree",
            "timing": "Applied in three split doses (Spring, Summer, Autumn)",
            "method": "Soil application + foliar micro-spray",
            "benefits": "Maintains tree productivity despite compromised vascular system.",
            "additional_supplement": "Iron, Zinc, Manganese chelate spray",
            "tips": ["Keep trees well-watered and well-fed to prolong productive lifespan if HLB is present."]
        },
        "cnn_agreement": True,
        "cnn_note": "Asymmetrical yellow leaf mottling is diagnostic for Huanglongbing."
    },

    # ═══════════════════════════════════════════════════
    # PEACH DISEASES
    # ═══════════════════════════════════════════════════
    "Peach___Bacterial_spot": {
        "plant_name": "Peach",
        "plant_scientific": "Prunus persica",
        "disease_name": "Bacterial Spot",
        "disease_pathogen": "Xanthomonas arboricola pv. pruni (Bacteria)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Shot-hole leaf spots indicate Bacterial Spot.",
        "symptoms": "Small, angular purple-brown spots on leaves. Spotted tissue falls out, creating 'shot-holes'. Sunken spots on fruit.",
        "description": "Bacterial Spot strikes peaches during warm, wet spring conditions. It causes premature leaf drop, weakens tree health, and leaves direct lesions on peaches, ruining market value.",
        "treatment": "Apply copper-based sprays during bud swell. Use oxytetracycline sprays in summer.",
        "prevention": "Avoid excessive nitrogen fertilization. Plant resistant peach varieties like Redhaven or Loring.",
        "medicine": {
            "name": "Copper Hydroxide or Oxytetracycline",
            "type": "Bactericide",
            "active_ingredient": "Copper Hydroxide or Oxytetracycline (Mycoshield)",
            "dose": "2g per litre of water (Copper) or 1.5g per litre (Oxytetracycline)",
            "frequency": "Weekly during wet spring periods from shuck split to harvest",
            "method": "Foliar Spray",
            "preharvest_interval": "21 days (Oxytetracycline), 0 days (Copper)",
            "safety": "Wear a dust mask during mixing. Wash skin immediately.",
            "alternatives": ["Bacillus amyloliquefaciens (Serenade)", "Copper octanoate"],
            "caution": "Repeated copper sprays on peach foliage in warm weather can cause severe leaf burn."
        },
        "fertilizer": {
            "name": "Slow-Release Nitrogen Fertilizer",
            "type": "Chemical",
            "npk_n": "10",
            "npk_p": "10",
            "npk_k": "10",
            "dose": "200g per young tree, up to 1kg for mature trees",
            "timing": "Early spring",
            "method": "Soil application",
            "benefits": "Maintains steady growth without spikes that attract bacterial pathogens.",
            "additional_supplement": "Calcium / Boron spray",
            "tips": ["Do not apply nitrogen fertilizers in late summer, which causes frost-susceptible growth."]
        },
        "cnn_agreement": True,
        "cnn_note": "Shot-hole appearance is highly characteristic of Peach Bacterial Spot."
    },

    # ═══════════════════════════════════════════════════
    # PEPPER DISEASES
    # ═══════════════════════════════════════════════════
    "Pepper,_bell___Bacterial_spot": {
        "plant_name": "Pepper (Bell)",
        "plant_scientific": "Capsicum annuum",
        "disease_name": "Bacterial Spot",
        "disease_pathogen": "Xanthomonas campestris pv. vesicatoria (Bacteria)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Angular dark spots on pepper leaf indicate Bacterial Spot.",
        "symptoms": "Small, dark, water-soaked spots on leaves. Spots turn brown with raised centers on leaf undersides. Leaves turn yellow and drop.",
        "description": "Bacterial Spot is a highly contagious bacterial disease of peppers. It spreads via rain splash and contaminated seeds, causing rapid defoliation and scarred fruit under hot, humid conditions.",
        "treatment": "Spray copper-based bactericides combined with mancozeb. Destroy infected plants immediately.",
        "prevention": "Use certified disease-free seeds. Avoid overhead irrigation. Practice crop rotation.",
        "medicine": {
            "name": "Copper Hydroxide + Mancozeb mix",
            "type": "Contact Bactericide / Protectant",
            "active_ingredient": "Copper Hydroxide (53.8%) + Mancozeb",
            "dose": "2g Copper + 1.5g Mancozeb per litre of water",
            "frequency": "Every 7-10 days in wet, warm weather",
            "method": "Foliar Spray",
            "preharvest_interval": "7 days",
            "safety": "Wear chemical-resistant gloves. Avoid inhalation.",
            "alternatives": ["Serenade ASO (Biological)", "Copper Octanoate"],
            "caution": "Copper-resistant strains of Xanthomonas exist; combine with Mancozeb to increase effectiveness."
        },
        "fertilizer": {
            "name": "Calcium-Rich Organic NPK",
            "type": "Organic",
            "npk_n": "4",
            "npk_p": "6",
            "npk_k": "8",
            "dose": "50g per plant",
            "timing": "Applied at transplanting and first flowering",
            "method": "Soil incorporation near root zone",
            "benefits": "Supports cell wall structure and helps prevent blossom end rot.",
            "additional_supplement": "Calcium nitrate / Epsom salts",
            "tips": ["Ensure magnesium and calcium are balanced to boost pepper leaf vigor."]
        },
        "cnn_agreement": True,
        "cnn_note": "Water-soaked brown leaf spots match Pepper Bacterial Spot profile."
    },

    # ═══════════════════════════════════════════════════
    # POTATO DISEASES
    # ═══════════════════════════════════════════════════
    "Potato___Early_blight": {
        "plant_name": "Potato",
        "plant_scientific": "Solanum tuberosum",
        "disease_name": "Early Blight",
        "disease_pathogen": "Alternaria solani (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Bullseye target-like leaf spots indicate Early Blight.",
        "symptoms": "Dark brown, circular spots with concentric rings ('bullseye' or 'target' pattern) on older leaves first.",
        "description": "Early Blight affects potato foliage and tubers. It starts on older lower leaves and spreads upward. Unlike late blight, it is less explosive but can cause severe leaf death and yield loss.",
        "treatment": "Apply chlorothalonil, mancozeb, or copper fungicides. Prune lower diseased leaves.",
        "prevention": "Rotate crops with non-solanaceous crops. Space plants well to dry foliage. Clean up plant debris.",
        "medicine": {
            "name": "Chlorothalonil or Azoxystrobin",
            "type": "Contact / Systemic Fungicide",
            "active_ingredient": "Chlorothalonil (500g/L)",
            "dose": "2 ml per litre of water",
            "frequency": "Every 7-10 days starting when plants are 6 inches tall",
            "method": "Foliar Spray",
            "preharvest_interval": "7 days",
            "safety": "Highly toxic if inhaled. Do not use without a proper mask.",
            "alternatives": ["Copper sulfate", "Bacillus amyloliquefaciens"],
            "caution": "Ensure thorough coverage of both upper and lower leaf surfaces."
        },
        "fertilizer": {
            "name": "High-Potassium / Potato Fertilizer Blend",
            "type": "Chemical",
            "npk_n": "10",
            "npk_p": "15",
            "npk_k": "20",
            "dose": "80g per square meter",
            "timing": "Applied at planting and hilling stages",
            "method": "Soil side-dressing",
            "benefits": "Improves starch production and strengthens tuber skin against rot.",
            "additional_supplement": "Magnesium sulfate (Epsom salts)",
            "tips": ["Avoid late-season nitrogen which delays tuber maturation and softens skins."]
        },
        "cnn_agreement": True,
        "cnn_note": "Concentric rings are classic identifiers for Early Blight."
    },

    "Potato___Late_blight": {
        "plant_name": "Potato",
        "plant_scientific": "Solanum tuberosum",
        "disease_name": "Late Blight",
        "disease_pathogen": "Phytophthora infestans (Oomycete)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Water-soaked dark spots with white fuzzy mold indicate Late Blight.",
        "symptoms": "Large, dark, water-soaked lesions on leaves and stems. White fuzzy fungal-like growth on leaf undersides in humid weather.",
        "description": "Late Blight is a catastrophic, highly destructive plant disease (responsible for the Irish Potato Famine). It spreads rapidly in cool, wet weather, destroying entire fields in days and rotting tubers.",
        "treatment": "Destroy infected plants immediately. Apply systemic fungicides like metalaxyl or copper protectants.",
        "prevention": "Plant only certified disease-free seed tubers. Avoid overhead watering. Kill vines before harvest.",
        "medicine": {
            "name": "Mefenoxam (Metalaxyl-M) or Copper Hydroxide",
            "type": "Systemic / Contact",
            "active_ingredient": "Mefenoxam or Copper Hydroxide (53.8%)",
            "dose": "2g per litre of water (Copper) or 1 ml per litre (Mefenoxam)",
            "frequency": "Every 5-7 days during high-risk cool, rainy periods",
            "method": "Foliar Spray",
            "preharvest_interval": "14 days (Mefenoxam), 0 days (Copper)",
            "safety": "Strict safety gear required. Wash clothing immediately after spraying.",
            "alternatives": ["Cymoxanil", "Propamocarb"],
            "caution": "Fungal resistance to Metalaxyl is high; always rotate or mix with copper/mancozeb."
        },
        "fertilizer": {
            "name": "Phosphite-Based Foliar Nutrient",
            "type": "Chemical",
            "npk_n": "0",
            "npk_p": "30",
            "npk_k": "20",
            "dose": "3 ml per litre of water",
            "frequency": "Foliar spray every 14 days",
            "method": "Foliar Spray",
            "benefits": "Phosphite ions trigger the potato plant's natural defense systems against oomycetes.",
            "additional_supplement": "Calcium nitrate",
            "tips": ["Keep potato tubers deeply buried (hilled) to protect them from spores washing down from leaves."]
        },
        "cnn_agreement": True,
        "cnn_note": "Large water-soaked lesions are highly characteristic of Late Blight."
    },

    # ═══════════════════════════════════════════════════
    # SQUASH DISEASES
    # ═══════════════════════════════════════════════════
    "Squash___Powdery_mildew": {
        "plant_name": "Squash",
        "plant_scientific": "Cucurbita pepo",
        "disease_name": "Powdery Mildew",
        "disease_pathogen": "Podosphaera xanthii (Fungus)",
        "is_healthy": False,
        "severity": "Mild",
        "confidence_note": "White talcum-like powder on squash leaf indicates Powdery Mildew.",
        "symptoms": "White, talcum-powder-like spots on leaves, stems, and petioles. Leaves turn yellow, dry out, and die.",
        "description": "Powdery Mildew is very common on cucurbits. It thrives in high humidity and warm temperatures, blocking sunlight and causing early leaf death, which leads to sunscalded squash fruit.",
        "treatment": "Spray neem oil, sulfur, or potassium bicarbonate. Remove heavily infected leaves.",
        "prevention": "Provide wide plant spacing. Grow in full sun. Plant resistant squash cultivars.",
        "medicine": {
            "name": "Potassium Bicarbonate or Sulfur",
            "type": "Contact Fungicide / Protectant",
            "active_ingredient": "Potassium Bicarbonate (85%) or Wettable Sulfur",
            "dose": "4g per litre of water",
            "frequency": "Every 7-10 days at first sign of white spots",
            "method": "Foliar Spray",
            "preharvest_interval": "0 days",
            "safety": "Wear basic eye protection. Safe for organic gardens.",
            "alternatives": ["Neem Oil", "Baking Soda + Liquid Soap spray"],
            "caution": "Do not spray sulfur or oils during temperatures exceeding 32°C (90°F) to avoid leaf scorch."
        },
        "fertilizer": {
            "name": "Compost-Based Nutrient Tea & Potassium Boost",
            "type": "Organic",
            "npk_n": "3",
            "npk_p": "3",
            "npk_k": "9",
            "dose": "100g per plant base",
            "timing": "Applied when vine begins to run and at fruiting",
            "method": "Soil application",
            "benefits": "Maintains leaf health and improves potassium levels for squash growth.",
            "additional_supplement": "Silicon-rich liquid fertilizer",
            "tips": ["Water the soil directly; do not wet squash leaves late in the evening."]
        },
        "cnn_agreement": True,
        "cnn_note": "White powdery coating matches Powdery Mildew symptoms."
    },

    # ═══════════════════════════════════════════════════
    # STRAWBERRY DISEASES
    # ═══════════════════════════════════════════════════
    "Strawberry___Leaf_scorch": {
        "plant_name": "Strawberry",
        "plant_scientific": "Fragaria × ananassa",
        "disease_name": "Leaf Scorch",
        "disease_pathogen": "Diplocarpon earlianum (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Purple blotches turning brown on leaf indicates Leaf Scorch.",
        "symptoms": "Irregular dark purple spots on leaves that turn brown/red and look 'scorched'. Leaves dry up and curl.",
        "description": "Leaf Scorch is a common fungal disease of strawberries. It attacks leaves, petioles, and stolons, reducing plant vigor and ruining runners during humid, wet spring and summer weather.",
        "treatment": "Remove old leaves after harvest. Apply copper fungicides or protective chemical fungicides.",
        "prevention": "Keep plants thinned to allow wind drying. Avoid over-fertilizing with nitrogen.",
        "medicine": {
            "name": "Copper Octanoate or Captan",
            "type": "Contact Fungicide",
            "active_ingredient": "Copper Octanoate (Soap-based)",
            "dose": "2.5 ml per litre of water",
            "frequency": "Every 10 days during warm, rainy spring months",
            "method": "Foliar Spray",
            "preharvest_interval": "0 days (Copper), 2 days (Captan)",
            "safety": "Wash strawberries thoroughly before eating.",
            "alternatives": ["Sulfur spray", "Bacillus subtilis"],
            "caution": "Do not apply soap-based copper sprays during peak noon heat."
        },
        "fertilizer": {
            "name": "Slow-Release Organic Strawberry Feed",
            "type": "Organic",
            "npk_n": "4",
            "npk_p": "6",
            "npk_k": "6",
            "dose": "30g per plant",
            "timing": "Early spring and immediately post-renovation",
            "method": "Side-dress under mulch",
            "benefits": "Supports steady growth and flower bud development.",
            "additional_supplement": "Bone meal / Kelp meal",
            "tips": ["Avoid overhead irrigation; use drip tapes or soaker hoses to keep leaves dry."]
        },
        "cnn_agreement": True,
        "cnn_note": "Purple-brown scorched leaf margins are indicative of Leaf Scorch."
    },

    # ═══════════════════════════════════════════════════
    # TOMATO DISEASES
    # ═══════════════════════════════════════════════════
    "Tomato___Bacterial_spot": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Bacterial Spot",
        "disease_pathogen": "Xanthomonas perforans (Bacteria)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Small dark spots with yellow halos match Tomato Bacterial Spot.",
        "symptoms": "Small, dark, irregular spots on leaves with yellow halos. Spots can merge, causing leaves to turn brown and die.",
        "description": "Bacterial Spot is a highly contagious disease affecting tomato leaves, stems, and fruit. It spreads via rain splash and warm, humid conditions, causing significant defoliation and sunscald.",
        "treatment": "Spray copper-based bactericides mixed with Mancozeb. Avoid working in wet fields.",
        "prevention": "Use certified seed. Rotate crops. Remove infected plant debris at season's end.",
        "medicine": {
            "name": "Copper Hydroxide + Mancozeb",
            "type": "Contact Bactericide / Fungicide Mix",
            "active_ingredient": "Copper Hydroxide (53.8%) + Mancozeb",
            "dose": "2g Copper + 1.5g Mancozeb per litre",
            "frequency": "Every 7-10 days in wet conditions",
            "method": "Foliar Spray",
            "preharvest_interval": "5 days",
            "safety": "Wear long pants, sleeves, and protective eyewear.",
            "alternatives": ["Serenade ASO (Bacillus amyloliquefaciens)", "Copper Soap"],
            "caution": "Bacteria can develop resistance to copper; always mix with Mancozeb for control."
        },
        "fertilizer": {
            "name": "Calcium Nitrate & Balanced NPK",
            "type": "Chemical",
            "npk_n": "15",
            "npk_p": "5",
            "npk_k": "15",
            "dose": "30g per plant",
            "timing": "Applied at transplanting and first fruit set",
            "method": "Soil side-dressing",
            "benefits": "Supports cell wall structure, helping plants resist bacterial entry.",
            "additional_supplement": "Calcium chloride spray",
            "tips": ["Ensure uniform soil watering to avoid blossom end rot and tissue split."]
        },
        "cnn_agreement": True,
        "cnn_note": "Leaf spots and yellow halos align with Bacterial Spot symptoms."
    },

    "Tomato___Early_blight": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Early Blight",
        "disease_pathogen": "Alternaria solani (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Target-like circular brown spots indicate Early Blight.",
        "symptoms": "Dark brown, circular spots with concentric target-board rings on older leaves first. Stem lesions and fruit rot.",
        "description": "Early Blight is a very common fungal disease of tomatoes. It progresses from the lower leaves upward, causing defoliation, stem girdling, and black rot at the stem end of fruits.",
        "treatment": "Prune lower leaves (up to 12 inches from ground). Apply chlorothalonil, mancozeb, or copper fungicides.",
        "prevention": "Mulch the soil under plants to prevent soil splash. Stake and cage tomatoes. Space plants well.",
        "medicine": {
            "name": "Chlorothalonil or Daconil",
            "type": "Contact Fungicide",
            "active_ingredient": "Chlorothalonil (500g/L)",
            "dose": "2 ml per litre of water",
            "frequency": "Every 7-10 days starting at transplanting",
            "method": "Foliar Spray",
            "preharvest_interval": "0 days (Chlorothalonil)",
            "safety": "Keep pets and children away until spray has dried completely.",
            "alternatives": ["Copper soap", "Actinovate (Biological)"],
            "caution": "Apply early in the morning or evening to prevent leaf burn."
        },
        "fertilizer": {
            "name": "High-Potassium Organic Tomato Feed",
            "type": "Organic",
            "npk_n": "3",
            "npk_p": "4",
            "npk_k": "6",
            "dose": "50g per plant",
            "timing": "Every 2 weeks after fruit set",
            "method": "Soil application",
            "benefits": "Maintains potassium levels for fruit growth and overall plant vigor.",
            "additional_supplement": "Seaweed extract foliar spray",
            "tips": ["Properly balanced nutrients prevent early defoliation from blight stress."]
        },
        "cnn_agreement": True,
        "cnn_note": "Concentric rings are highly diagnostic for Early Blight."
    },

    "Tomato___Late_blight": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Late Blight",
        "disease_pathogen": "Phytophthora infestans (Oomycete)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Large water-soaked spots and white mold indicate Late Blight.",
        "symptoms": "Large, dark water-soaked spots on leaves and stems. White, fuzzy spore growth on leaf undersides in humid conditions. Large leathery brown spots on green fruit.",
        "description": "Late Blight is a destructive oomycete disease. It thrives in cool, wet weather and spreads rapidly via wind-blown spores, capable of destroying healthy tomato plants and fruit in a matter of days.",
        "treatment": "Destroy infected plants. Apply specialized systemic fungicides like mefenoxam or copper protectants.",
        "prevention": "Grow resistant cultivars (e.g., Defiant, Mountain Merit). Avoid planting near potatoes. Avoid overhead irrigation.",
        "medicine": {
            "name": "Mefenoxam or Copper Hydroxide",
            "type": "Systemic / Contact Fungicide",
            "active_ingredient": "Copper Hydroxide (53.8%)",
            "dose": "2g per litre of water",
            "frequency": "Every 5-7 days during cool, rainy periods",
            "method": "Foliar Spray",
            "preharvest_interval": "0 days (Copper)",
            "safety": "Wear personal protective equipment (goggles, mask, gloves).",
            "alternatives": ["Chlorothalonil", "Revus (Mandipropamid)"],
            "caution": "Late Blight spreads so fast that delayed spraying will result in complete plant loss."
        },
        "fertilizer": {
            "name": "Potassium Phosphite foliar feed",
            "type": "Chemical",
            "npk_n": "0",
            "npk_p": "28",
            "npk_k": "26",
            "dose": "3 ml per litre of water",
            "frequency": "Every 14 days during high-risk periods",
            "method": "Foliar Spray",
            "benefits": "Triggers systemic acquired resistance (SAR) in tomatoes to resist oomycete attack.",
            "additional_supplement": "Calcium nitrate",
            "tips": ["Remove and bury or bag infected plants; do not throw them in compost piles."]
        },
        "cnn_agreement": True,
        "cnn_note": "Large water-soaked leaf spots match Late Blight diagnosis."
    },

    "Tomato___Leaf_Mold": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Leaf Mold",
        "disease_pathogen": "Passalora fulva (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Olive-green velvet mold under leaf indicates Leaf Mold.",
        "symptoms": "Pale green/yellow spots on upper leaf surfaces. Olive-green to purple velvety fungal growth on matching under-leaf surfaces.",
        "description": "Leaf Mold primarily occurs in greenhouse tomatoes or high tunnels with high humidity and poor ventilation. It causes leaf yellowing, drying, and early leaf drop.",
        "treatment": "Increase ventilation and reduce humidity. Apply chlorothalonil or copper fungicides.",
        "prevention": "Grow mold-resistant varieties. Use fans and open vents in greenhouses. Prune plants to improve airflow.",
        "medicine": {
            "name": "Chlorothalonil or Copper octanoate",
            "type": "Contact Fungicide",
            "active_ingredient": "Chlorothalonil",
            "dose": "2 ml per litre of water",
            "frequency": "Every 7-10 days if greenhouse humidity exceeds 85%",
            "method": "Foliar Spray",
            "preharvest_interval": "0 days",
            "safety": "Ensure proper mask and eye protection during greenhouse spraying.",
            "alternatives": ["Serenade ASO", "Sulfur spray"],
            "caution": "Fungicide application must thoroughly coat the undersides of leaves where the fungus grows."
        },
        "fertilizer": {
            "name": "Low-Nitrogen / Soluble Tomato Fertilizer",
            "type": "Chemical",
            "npk_n": "5",
            "npk_p": "15",
            "npk_k": "30",
            "dose": "1g per litre of water",
            "frequency": "Weekly via fertigation (drip)",
            "method": "Drip irrigation drench",
            "benefits": "Maintains high potassium and phosphorus without excess nitrogen foliage growth.",
            "additional_supplement": "Magnesium sulfate (Epsom salts)",
            "tips": ["Prune out suckers and lower leaves to allow sunlight to dry the lower canopy."]
        },
        "cnn_agreement": True,
        "cnn_note": "Olive-green velvet fungal backing matches Leaf Mold characteristics."
    },

    "Tomato___Septoria_leaf_spot": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Septoria Leaf Spot",
        "disease_pathogen": "Septoria lycopersici (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Tiny spots with grey centers and black specks indicate Septoria.",
        "symptoms": "Numerous small, circular spots with dark borders and grey/tan centers. Tiny black specks (pycnidia) inside spots.",
        "description": "Septoria is one of the most common foliage diseases of tomatoes. It starts on lower leaves after rain splash and works upward, causing severe yellowing and defoliation but does not directly infect fruit.",
        "treatment": "Mulch plants. Remove infected lower leaves. Spray mancozeb, chlorothalonil, or copper fungicides.",
        "prevention": "Rotate crops. Avoid overhead watering. Cage tomatoes to keep leaves off ground. Control weeds.",
        "medicine": {
            "name": "Mancozeb or Daconil",
            "type": "Contact Protectant Fungicide",
            "active_ingredient": "Mancozeb (75% WP)",
            "dose": "2g per litre of water",
            "frequency": "Every 7-10 days in wet summer weather",
            "method": "Foliar Spray",
            "preharvest_interval": "5 days",
            "safety": "Wear protective gloves and long sleeves.",
            "alternatives": ["Copper octanoate", "Sulfur spray"],
            "caution": "Wash fruit thoroughly before consumption."
        },
        "fertilizer": {
            "name": "Organic Fish & Kelp Emulsion",
            "type": "Organic",
            "npk_n": "2",
            "npk_p": "4",
            "npk_k": "1",
            "dose": "15 ml per litre of water",
            "frequency": "Drench every 2 weeks",
            "method": "Soil Drench",
            "benefits": "Supports plant regeneration and foliage recovery from lower leaf loss.",
            "additional_supplement": "Calcium nitrate",
            "tips": ["Mulch with straw or plastic to prevent Septoria spores in the soil from splashing onto leaves."]
        },
        "cnn_agreement": True,
        "cnn_note": "Grey-centered tiny spots are typical of Septoria Leaf Spot."
    },

    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Two-Spotted Spider Mite Damage",
        "disease_pathogen": "Tetranychus urticae (Pest)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Foliar speckling and fine webbing indicate Spider Mites.",
        "symptoms": "Fine yellow speckling (stippling) on leaves. Yellow/bronze dry leaves with fine webbing on undersides. Stunted plants.",
        "description": "Spider Mites are tiny pests that suck leaf sap, destroying chlorophyll. They multiply rapidly in hot, dry weather and can quickly kill leaves and weaken the plant, causing fruit drop.",
        "treatment": "Spray horticultural soap, neem oil, or miticides. Mist plants with water to disrupt webs.",
        "prevention": "Avoid dusty conditions. Keep plants well-watered. Encourage natural predators like ladybugs.",
        "medicine": {
            "name": "Abamectin or Insecticidal Soap",
            "type": "Miticide / Contact Soap",
            "active_ingredient": "Abamectin (1.8% EC) or Potassium salts of fatty acids",
            "dose": "0.5 ml per litre (Abamectin) or 10 ml per litre (Soap)",
            "frequency": "Every 5-7 days (3 times to break egg cycle)",
            "method": "Foliar Spray (Thorough coverage under leaves)",
            "preharvest_interval": "7 days (Abamectin), 0 days (Soap)",
            "safety": "Avoid contact with skin. Wear goggles during spray.",
            "alternatives": ["Neem Oil", "Spinosad"],
            "caution": "Spider mites develop resistance to miticides very fast. Do not use chemical miticides consecutively."
        },
        "fertilizer": {
            "name": "Humic Acid and Seaweed Kelp Meal",
            "type": "Organic",
            "npk_n": "1",
            "npk_p": "0",
            "npk_k": "2",
            "dose": "10 ml per litre of water",
            "frequency": "Weekly foliar spray",
            "method": "Foliar Spray",
            "benefits": "Reduces transplant stress and assists leaves in recovering from feeding puncture wounds.",
            "additional_supplement": "Silicon nutrients",
            "tips": ["Avoid high nitrogen fertilizers, which create succulent leaf sap that spider mites prefer."]
        },
        "cnn_agreement": True,
        "cnn_note": "Yellow stippling and webbing are diagnostic for Spider Mites."
    },

    "Tomato___Target_Spot": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Target Spot",
        "disease_pathogen": "Corynespora cassiicola (Fungus)",
        "is_healthy": False,
        "severity": "Moderate",
        "confidence_note": "Target-like spots with clear yellow halos indicate Target Spot.",
        "symptoms": "Zonate circular spots with light brown centers and dark rings, surrounded by prominent yellow halos on leaves.",
        "description": "Target Spot is a fungal disease that causes leaf spotting, stem lesions, and fruit rot. It thrives in high humidity and warm temperatures, causing severe defoliation of the lower tomato canopy.",
        "treatment": "Apply strobilurin or carboxamide fungicides. Prune lower canopy leaves.",
        "prevention": "Maintain wider plant spacing for rapid drying. Stake vines. Keep fields weed-free.",
        "medicine": {
            "name": "Azoxystrobin or Boscalid",
            "type": "Systemic Fungicide",
            "active_ingredient": "Azoxystrobin (250 SC)",
            "dose": "1 ml per litre of water",
            "frequency": "Every 10-14 days starting at first sign of target spots",
            "method": "Foliar Spray",
            "preharvest_interval": "1 day (Azoxystrobin)",
            "safety": "Keep away from aquatic environments. Wear basic protective gear.",
            "alternatives": ["Copper octanoate", "Chlorothalonil"],
            "caution": "Rotate fungicides with different modes of action to prevent resistance development."
        },
        "fertilizer": {
            "name": "High-Potassium / High-Calcium Tomato Feed",
            "type": "Chemical",
            "npk_n": "8",
            "npk_p": "16",
            "npk_k": "36",
            "dose": "30g per plant",
            "timing": "Applied at bloom and fruiting",
            "method": "Soil application",
            "benefits": "Fosters strong stem growth and cell wall resistance against fungal invasion.",
            "additional_supplement": "Chelated Calcium spray",
            "tips": ["Pruning suckers and lower leaves is essential to prevent microclimates that foster target spot."]
        },
        "cnn_agreement": True,
        "cnn_note": "Concentric spots with yellow halos indicate Target Spot."
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "disease_pathogen": "Begomovirus (Virus)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Cup-like yellowing leaves indicate TYLCV.",
        "symptoms": "Leaves are small, yellow, and curl upward in a cup-like shape. Severe stunting of plant growth. Flowers drop, resulting in no fruit.",
        "description": "TYLCV is a devastating viral disease transmitted by the Silverleaf Whitefly. Once a plant is infected, there is no cure. The plant stops growing and fails to produce marketable fruit.",
        "treatment": "No chemical cure. Remove and destroy infected plants immediately. Control the Whitefly vector.",
        "prevention": "Grow whitefly-resistant tomato varieties. Use insect netting in greenhouses. Monitor with yellow sticky cards.",
        "medicine": {
            "name": "Imidacloprid or Acetamiprid (for Whitefly vector control)",
            "type": "Systemic Insecticide",
            "active_ingredient": "Imidacloprid (200 SL)",
            "dose": "0.5 ml per litre of water",
            "frequency": "Foliar spray at first whitefly detection. Repeat in 10 days if needed.",
            "method": "Foliar Spray / Soil Drench",
            "preharvest_interval": "7 days",
            "safety": "Avoid spraying near beehives or when beneficial insects are active.",
            "alternatives": ["Neem Oil", "Pyrethrins"],
            "caution": "Control of whiteflies is the only way to manage this virus. Infected plants must be bagged and burnt."
        },
        "fertilizer": {
            "name": "Seaweed Extract and Humic Acids",
            "type": "Organic",
            "npk_n": "2",
            "npk_p": "2",
            "npk_k": "5",
            "dose": "15 ml per litre of water",
            "frequency": "Drench weekly",
            "method": "Soil application",
            "benefits": "Supports survival of uninfected surrounding plants and boosts general stress tolerance.",
            "additional_supplement": "Root development bio-stimulants",
            "tips": ["Keep weeds controlled as they can act as alternative hosts for whiteflies and the virus."]
        },
        "cnn_agreement": True,
        "cnn_note": "Upward curling yellow leaves are highly diagnostic for TYLCV."
    },

    "Tomato___Tomato_mosaic_virus": {
        "plant_name": "Tomato",
        "plant_scientific": "Solanum lycopersicum",
        "disease_name": "Tomato Mosaic Virus (ToMV)",
        "disease_pathogen": "Tobamovirus (Virus)",
        "is_healthy": False,
        "severity": "Severe",
        "confidence_note": "Mottled mosaic patterns on leaves indicate ToMV.",
        "symptoms": "Mottled yellow-green 'mosaic' or 'fern-leaf' patterns on leaves. Leaf distortion, blistering, and puckering.",
        "description": "Tomato Mosaic Virus is an extremely stable virus that can survive for years in soil, plant debris, and on tools. It is spread mechanically by hands, tools, and clothing during handling, leading to poor fruit development.",
        "treatment": "No chemical treatment. Pull and burn infected plants. Disinfect tools and hands in skim milk or trisodium phosphate.",
        "prevention": "Plant certified virus-free seeds or resistant cultivars. Wash hands and tools frequently.",
        "medicine": {
            "name": "Trisodium Phosphate (TSP) or Skim Milk (for mechanical disinfection)",
            "type": "Disinfectant",
            "active_ingredient": "Trisodium Phosphate (10% solution) or Skim milk powder",
            "dose": "Dip tools in 10% TSP solution",
            "frequency": "Before and after working on each plant",
            "method": "Tool dip and hand wash",
            "preharvest_interval": "N/A",
            "safety": "Wear gloves when handling TSP; it is highly alkaline and can irritate skin.",
            "alternatives": ["Virkon-S disinfectant", "Household bleach (10% solution)"],
            "caution": "ToMV is extremely stable and can be spread just by touching an infected leaf and then a healthy one."
        },
        "fertilizer": {
            "name": "Organic Compost & Trace Mineral Blend",
            "type": "Organic",
            "npk_n": "5",
            "npk_p": "5",
            "npk_k": "5",
            "dose": "500g per plant",
            "timing": "Applied to soil before transplanting",
            "method": "Soil incorporation",
            "benefits": "Improves organic matter and enhances natural crop immune systems.",
            "additional_supplement": "Mycorrhizal fungi inoculants",
            "tips": ["Do not smoke near tomatoes, as tobacco products can transmit Tobacco/Tomato Mosaic Virus."]
        },
        "cnn_agreement": True,
        "cnn_note": "Fern-leaf puckering and mosaic patterns match Tomato Mosaic Virus symptoms."
    }
}
