import math

# Constants
lifetime = 60
calibration = 8760 / 7446
designs = {
    "EPR": {"capacity": 1650, "construction_cost": 4013, "fuel_cycle": 70, "fixed_operations": 96},
    "ABWR": {"capacity": 1152, "construction_cost": 3963, "fuel_cycle": 103, "fixed_operations": 173},
    "APR1400": {"capacity": 1377, "construction_cost": 2157, "fuel_cycle": 70, "fixed_operations": 124},
    "AP1000": {"capacity": 1100, "construction_cost": 4250, "fuel_cycle": 70, "fixed_operations": 68},
    "VVER": {"capacity": 1122, "construction_cost": 2271, "fuel_cycle": 37, "fixed_operations": 76},
    "CAP1400": {"capacity": 1400, "construction_cost": 2500, "fuel_cycle": 75, "fixed_operations": 177},
    "PHWR": {"capacity": 700, "construction_cost": 2778, "fuel_cycle": 70, "fixed_operations": 160}
}

# Get user inputs
while True:
    design_choice = input("Would you like to select a design? (y/n): ")
    if design_choice.lower() == 'y':
        print("Available designs: ", ", ".join(designs.keys()))
        selected_design = input("Enter the name of the selected design: ")
        if selected_design in designs:
            design = designs[selected_design]
            capacity = design["capacity"]
            construction_cost = design["construction_cost"]
            fuel_cycle = design["fuel_cycle"]
            fixed_operations = design["fixed_operations"]
            break
        else:
            print("Invalid design selection, please try again.")
    elif design_choice.lower() == 'n':
        # Show available designs' characteristics
        print("Available designs and their characteristics:")
        for design, values in designs.items():
            print(f"{design}:")
            print(f"\tCapacity: {values['capacity']} MW")
            print(f"\tConstruction Cost: €{values['construction_cost']}/kW")
            print(f"\tFuel Cycle at 85% CF: €{values['fuel_cycle']}/kW")
            print(f"\tFixed Operations: €{values['fixed_operations']}/kW")
        # Get user inputs
        capacity = float(input("Power plant capacity in MW: "))
        construction_cost = float(input(f"Overnight construction costs (€/kW): "))
        fuel_cycle = float(input(f"Annual front and back-end fuel costs at 85% CF (€/kW): "))
        fixed_operations = float(input(f"Annual fixed operations and management costs (€/kW): "))
        break
    else:
        print("Invalid input, please try again.")

discount_rate = float(input("Discount rate: "))
escalation_rate = float(input("Escalation rate: "))
construction_time = int(input("Construction lead time in years: "))
utilization_hours = float(input("Power plant utilization hours in a year: "))

# Constants
lifetime = 60
kW_MW = 1000 * capacity
calibration = utilization_hours / 7446

# Calculate CAPITAL
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
