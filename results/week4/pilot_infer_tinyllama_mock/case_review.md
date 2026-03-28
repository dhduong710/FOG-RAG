# Day 4 Pilot Inference Case Review

## Key Note
- Because the week-4 pilot still uses the week-2 mock coarse ranker (gold fixed at rank 1), MRR / Hits@K here are sanity-only and not scientific.

## Valid Metrics
- {'num_samples': 100, 'exact_match': 1.0, 'mrr': 1.0, 'hits1': 1.0, 'hits3': 1.0, 'hits10': 1.0, 'avg_subgraph_size': 74.15, 'all_coarse_rank_is_one': True}

## Test Metrics
- {'num_samples': 100, 'exact_match': 1.0, 'mrr': 1.0, 'hits1': 1.0, 'hits3': 1.0, 'hits10': 1.0, 'avg_subgraph_size': 73.63, 'all_coarse_rank_is_one': True}

## Valid - Correct Cases
### 1. Query: ovarian endometrioid adenocarcinoma
- target: Paclitaxel
- pred: Paclitaxel
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 72
- candidate_top5: ['Paclitaxel', 'Cerivastatin', 'Eptifibatide', 'Tinidazole', 'Lesinurad']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Paclitaxel', 'Cerivastatin', 'Eptifibatide', 'Tinidazole', 'Lesinurad', 'Diazoxide', 'Buclizine', 'Dichlorophen', 'Mepolizumab', 'Auranofin', 'Medrysone', 'Dehydrocholic acid', 'Clonazepam', 'Bosutinib', 'Paramethadione', 'Ripasudil', 'Escit`

### 2. Query: periarthritis
- target: Triamcinolone
- pred: Triamcinolone
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 80
- candidate_top5: ['Triamcinolone', 'Metharbital', 'Irinotecan', 'Ethionamide', 'Levamisole']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Triamcinolone', 'Metharbital', 'Irinotecan', 'Ethionamide', 'Levamisole', 'Cloxacillin', 'Chloral hydrate', 'Mepolizumab', 'Itopride', 'Rotigotine', 'Trastuzumab', 'Diflunisal', 'Lutein', 'Belotecan', 'Salicylamide', 'Miltefosine', 'Sonidegi`

### 3. Query: conjunctivitis
- target: Demeclocycline
- pred: Demeclocycline
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 78
- candidate_top5: ['Demeclocycline', 'Acetohydroxamic acid', 'Mebeverine', 'Sildenafil', 'Triprolidine']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Demeclocycline', 'Acetohydroxamic acid', 'Mebeverine', 'Sildenafil', 'Triprolidine', 'Simeprevir', 'Chlorpromazine', 'Colistin', 'Tretamine', 'Povidone K30', 'Migalastat', 'Colchicine', 'Clomipramine', 'Norepinephrine', 'Trepibutone', 'Turoc`

### 4. Query: seborrheic dermatitis
- target: Ciclopirox
- pred: Ciclopirox
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 78
- candidate_top5: ['Ciclopirox', 'Prucalopride', 'Guanethidine', 'Polidocanol', 'Sivelestat']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Ciclopirox', 'Prucalopride', 'Guanethidine', 'Polidocanol', 'Sivelestat', 'Oxytetracycline', 'Glyburide', 'Glycine', 'Velpatasvir', 'Vandetanib', 'Isosorbide', 'Cefotaxime', 'Cinoxacin', 'Lonidamine', 'Didanosine', 'Mestranol', 'Lincomycin',`

### 5. Query: yaws
- target: Ceftriaxone
- pred: Ceftriaxone
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 86
- candidate_top5: ['Ceftriaxone', 'Ergoloid mesylate', 'Testosterone cypionate', 'Baloxavir marboxil', 'Vorinostat']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Ceftriaxone', 'Ergoloid mesylate', 'Testosterone cypionate', 'Baloxavir marboxil', 'Vorinostat', 'Phenylbutyric acid', 'Amyl Nitrite', 'Risedronic acid', 'Trilostane', 'Bendamustine', 'Ranitidine', 'Aflibercept', 'Vitamin A', 'Phenmetrazine'`


## Valid - Wrong Cases
- none

## Test - Correct Cases
### 1. Query: pharyngitis
- target: Codeine
- pred: Codeine
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 76
- candidate_top5: ['Codeine', 'Tocilizumab', 'Perospirone', 'Ivacaftor', 'Rutin']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Codeine', 'Tocilizumab', 'Perospirone', 'Ivacaftor', 'Rutin', 'Spironolactone', 'Elbasvir', 'Tinzaparin', 'Mechlorethamine', 'Amitriptyline', 'Histamine', 'Zolpidem', 'Polidocanol', 'Oxazepam', 'Levosalbutamol', 'Nelarabine', 'Simeprevir', '`

### 2. Query: hypertension
- target: Spironolactone
- pred: Spironolactone
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 64
- candidate_top5: ['Spironolactone', 'Acrivastine', 'Sirolimus', 'Temocapril', 'Somatotropin']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Spironolactone', 'Acrivastine', 'Sirolimus', 'Temocapril', 'Somatotropin', 'Fluorometholone', 'Axitinib', 'Perindopril', 'Promethazine', 'Nedocromil', 'Selumetinib', 'Levmetamfetamine', 'Sulfinpyrazone', 'Estrone', 'Empagliflozin', 'Etacryni`

### 3. Query: early-onset parkinsonism-intellectual disability syndrome
- target: Opicapone
- pred: Opicapone
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 68
- candidate_top5: ['Opicapone', 'Salbutamol', 'Dorzolamide', 'Delapril', 'Colestilan chloride']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Opicapone', 'Salbutamol', 'Dorzolamide', 'Delapril', 'Colestilan chloride', 'Pimozide', 'Afamelanotide', 'Avelumab', 'Polythiazide', 'Brigatinib', 'Azatadine', 'Simeprevir', 'Phenoxymethylpenicillin', 'Ceftolozane', 'Palivizumab', 'Efavirenz`

### 4. Query: seborrheic keratosis
- target: Selenium Sulfide
- pred: Selenium Sulfide
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 81
- candidate_top5: ['Selenium Sulfide', 'Teriflunomide', 'Cefaclor', 'Imipramine', 'Leucovorin']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Selenium Sulfide', 'Teriflunomide', 'Cefaclor', 'Imipramine', 'Leucovorin', 'Phenmetrazine', 'Tamsulosin', 'Testosterone enanthate', 'Oxprenolol', 'Iguratimod', 'Apalutamide', 'Ibalizumab', 'Fumaric Acid', 'Buspirone', 'Susoctocog alfa', 'Ef`

### 5. Query: skin disease
- target: Prednisolone
- pred: Prednisolone
- coarse_rank: 1
- pred_rank: 1
- subgraph_size: 80
- candidate_top5: ['Prednisolone', 'Enfuvirtide', 'Miltefosine', 'Rizatriptan', 'Eflornithine']
- input_preview: `You are a biomedical scientist. The task is to predict the answer based on the given question, and you only need to answer one entity. The answer must be in ('Prednisolone', 'Enfuvirtide', 'Miltefosine', 'Rizatriptan', 'Eflornithine', 'Ibuprofen', 'Lesinurad', 'Lapatinib', 'Temazepam', 'Adalimumab', 'Riboflavin', 'Lucinactant', 'Histrelin', 'Cetilistat', 'Vedolizumab', 'Cilastatin', 'Topotecan', '`


## Test - Wrong Cases
- none
