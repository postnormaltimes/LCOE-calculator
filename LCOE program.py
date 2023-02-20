import math

# Get user inputs
construction_cost = float(input("Overnight construction costs per kW: "))
discount_rate = float(input("Discount rate: "))
escalation_rate = float(input("Escalation rate: "))
construction_time = int(input("Construction lead time in years: "))
utilization_hours = float(input("Power plant utilization hours in a year: "))
capacity = float(input("Power plant capacity in MW: "))
lifetime = int(input("Power plant lifetime in years: "))
fixed_operations = float(input("Annual fixed operations and management costs per kW: "))
fuel_cycle = float(input("Annual front and back-end fuel costs per kW (at 85% capacity factor): "))

# Calculate CAPITAL
kW_MW = 1000 * capacity
calibration = utilization_hours / 7446
recovery_factor = (discount_rate * math.pow(1 + discount_rate, lifetime)) / (math.pow(1 + discount_rate, lifetime) - 1)
capital_costs = (construction_cost * kW_MW / construction_time) * sum([math.pow(1 + escalation_rate, t + 0.5) * math.pow(1 + discount_rate, construction_time - t) for t in range(0, construction_time)])
annual_capital_charge = capital_costs * recovery_factor
annual_electricity_production = utilization_hours * capacity
CAPITAL = annual_capital_charge / annual_electricity_production

# Calculate FOM
FOM = fixed_operations * kW_MW / annual_electricity_production

# Calculate VOM
VOM = fixed_operations * kW_MW * calibration / (9 * 7446 * capacity)

# Calculate FUEL
FUEL = fuel_cycle * kW_MW * calibration / (7446 * capacity)

# Calculate DECOMMISSIONING
decommissioning_fund = construction_cost * 0.15
DECOMMISSIONING = ((decommissioning_fund * kW_MW * 0.01) / (math.pow(1.01, lifetime) - 1)) / annual_electricity_production

# Calculate LCOE
LCOE = CAPITAL + FOM + VOM + FUEL + DECOMMISSIONING
print(f"LCOE = €{CAPITAL:.2f}/MWh + €{FOM:.2f}/MWh + €{VOM:.2f}/MWh + €{FUEL:.2f}/MWh + €{DECOMMISSIONING:.2f}/MWh = €{LCOE:.2f}/MWh")
