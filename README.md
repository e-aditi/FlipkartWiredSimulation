This code includes simulation files used to evaluate the idea for Flipkart case study. Model is the main folder and Model2 is a trail version of the code.
-------

## Algorithm Flow

### 1. SYSTEM INITIALIZATION
### 1.1 City Profile Setup
- Load predefined city metadata (Delhi, Pune)
- Each city has:
  - Average zone size (dark store coverage area = π × 3² km²)
  - Base delivery time (8-10 minutes)
  - Total area in sq km
  - Total available riders

### 1.2 Zone Generation
- Calculate number of zones: `zones = city_area / avg_zone_size`
- For each zone:
  - Assign random traffic level (low/moderate/high)
  - Generate 50-200 customers per zone
  - Distribute total city riders across zones (minimum 1 rider per zone)

### 2. CUSTOMER & RIDER CREATION

### 2.1 Customer Generation
- For each zone, create customers with:
  - Unique ID (Zone_X_CY format)
  - Random wallet status (True/False)
  - Random wishlist items (1-5 items)
  - Empty shopping cart

### 2.2 Rider Allocation
- Create fixed riders distributed across zones
- Each rider has:
  - Unique ID (Zone_X_RY or Zone_X_ODY for on-demand)
  - Zone assignment
  - Availability status
  - Order delivery counter (max 20 orders/day)

### 3. SCENARIO SELECTION & CONFIGURATION

### 3.1 User Input Processing
- Display available cities with zone count and rider information
- Present scenario options:
  - Business As Usual (BAU) - 1.0x multiplier
  - Peak Hours (Morning/Evening) - 1.08x multiplier
  - Peak Days (Fri-Sun) - 1.22x multiplier
  - Event/Sale Days - 1.45x multiplier
  - Peak Hour Event - 3.0x multiplier
  - Yearly Analysis (all scenarios)

### 3.2 Volume Multiplier Calculation
- Base volume multiplier assigned based on scenario
- Additional time-specific adjustments for peak hours
- Traffic factor calculated from zone traffic level

### 4. ORDER GENERATION PROCESS

### 4.1 Probability Calculation
- Base probabilities by scenario:
  - BAU: 35%
  - Peak Hours: 25% (with time-slot multipliers)
  - Peak Days: 30%
  - Event/Sale: 45%
  - Peak Hour Event: 60%

### 4.2 Customer Order Logic
- For each customer in each zone:
  - Apply scenario-specific probability
  - Check customer eligibility (wallet status, scenario rules)
  - Generate order items based on scenario:
    - BAU: 1-3 items (40% from wishlist)
    - Events: 2-6 items (70% from wishlist)
    - Peak Days: 1-4 items (50% from wishlist)
  - Determine if order is scheduled (10-30% based on scenario)

### 4.3 Order Object Creation
- Create Order instances with:
  - Customer reference
  - Items list
  - Scheduled flag
  - Timestamp
  - Delivery time (initially null)
  - Assigned rider (initially null)

### 5. DYNAMIC RIDER MANAGEMENT

### 5.1 On-Demand Rider Addition
- Check total city-wide orders
- If orders > 300: Add 1 on-demand rider per zone
- On-demand riders cost ₹500/day vs ₹400/day for fixed riders

### 6. ORDER ASSIGNMENT PROCESS

### 6.1 Rider Availability Check
- For each order in zone:
  - Find available riders (not at 20-order capacity)
  - Apply load balancing (assign to rider with fewer orders)
  - Mark rider as assigned to order

### 6.2 Delivery Time Calculation
- Start with base delivery time (8-10 minutes by city)
- Apply scenario multipliers:
  - Peak Hour Event: 2.5x
  - Event/Sale: 1.8x
  - Peak Days: 1.4x
  - Peak Hours: 1.2-1.3x
- Apply traffic factor (1.0-1.5x based on zone traffic)
- Add random variation (-1 to +3 minutes)
- Set order delivery timestamp

### 6.3 Unassigned Order Handling
- Orders without available riders → unassigned queue
- Track unassigned orders for capacity analysis

### 7. KPI COMPUTATION

### 7.1 Order Metrics
- Total Orders per zone
- Assigned vs Unassigned orders
- SLA compliance (deliveries < 10 minutes)
- Assignment rate percentage

### 7.2 Rider Metrics
- Utilization: (delivered orders / (riders × 20)) × 100%
- Average Orders Per Hour (OPH): delivered / (riders × 8 hours)
- Fixed vs On-demand rider counts

### 7.3 Cost Calculation
- Fixed rider cost: ₹400/day per rider
- On-demand rider cost: ₹500/day per rider
- Variable cost: ₹15 per delivered order
- Cost per delivery = total cost / assigned orders

### 8. RESULTS PROCESSING & DISPLAY

### 8.1 Zone-level Results
- Generate DataFrame with KPIs for each zone
- Display detailed metrics table:
  - Orders, assignments, SLA performance
  - Rider utilization, costs

### 8.2 City-level Aggregation
- Sum total orders, assignments across zones
- Calculate city-wide averages for:
  - Assignment rate
  - SLA performance
  - Rider utilization
  - Cost per delivery

### 9. YEARLY PATTERN ANALYSIS (Optional)

### 9.1 Multi-scenario Simulation
- Run simulations for all scenario types
- Apply yearly breakdown:
  - 196 BAU days
  - 156 peak days (Fri-Sun)
  - 12 sale days
  - 1 big event day

### 9.2 Annual Projections
- Calculate total yearly order volume
- Compare scenario performance metrics
- Generate cost and capacity recommendations

### 10. ITERATIVE EXECUTION

### 10.1 User Interaction Loop
- Display results in formatted tables
- Offer option to run additional simulations
- Handle different cities and scenarios
- Allow exit or continuation

### 10.2 Error Handling
- Validate user inputs
- Handle missing city data
- Manage rider capacity constraints
- Catch and report simulation errors
## Key Design Patterns:
**Capacity-Constrained Assignment**: Riders limited to 20 orders/day maximum
**Dynamic Scaling**: On-demand riders added when city orders > 300
**Scenario-Based Modeling**: Different order generation patterns by business context
**Load Balancing**: Orders distributed evenly across available riders
**Cost Optimization**: Balance fixed vs on-demand rider costs with service levels
