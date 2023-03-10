import math

designs = {
    "EPR": {"overnight_cost": 4013, "fuel_cycle": 70, "fixed_operations": 96},
    "ABWR": {"overnight_cost": 3963, "fuel_cycle": 103, "fixed_operations": 173},
    "APR1400": {"overnight_cost": 2157, "fuel_cycle": 70, "fixed_operations": 124},
    "AP1000": {"overnight_cost": 4250, "fuel_cycle": 70, "fixed_operations": 77},
    "VVER": {"overnight_cost": 2271, "fuel_cycle": 37, "fixed_operations": 68},
    "CAP1400": {"overnight_cost": 2500, "fuel_cycle": 75, "fixed_operations": 177},
    "PHWR": {"overnight_cost": 2778, "fuel_cycle": 70, "fixed_operations": 160},
    "Harmonized": {"overnight_cost": 3133, "fuel_cycle": 70, "fixed_operations": 125}
}

# Get user inputs
while True:
    # Available designs' characteristics
    show_char = input("Would you like to see available designs and their characteristics? (y/n): ")
    if show_char.lower() == 'y':
        print("Available designs and their characteristics:")
        for design, values in designs.items():
            print(f"{design}:")
            print(f"\tConstruction Cost: €{values['overnight_cost']}/kW")
            print(f"\tFuel Cycle at 85% CF: €{values['fuel_cycle']}/kW")
            print(f"\tFixed Operations: €{values['fixed_operations']}/kW")
        design_choice = input("Would you like to select a design? (y/n): ")
        if design_choice.lower() == 'y':
            print("Available designs: ", ", ".join(designs.keys()))
            selected_design = input("Enter the name of the selected design: ")
            if selected_design in designs:
                design = designs[selected_design]
                overnight_cost = design["overnight_cost"]
                fuel_cycle = design["fuel_cycle"]
                fixed_operations = design["fixed_operations"]
                break
            else:
                print("Invalid design selection, please try again.")
        elif design_choice.lower() == 'n':
            # Get user inputs
            overnight_cost = float(input(f"Overnight construction costs (€/kW): "))
            fuel_cycle = float(input(f"Annual front and back-end fuel costs at 85% CF (€/kW): "))
            fixed_operations = float(input(f"Annual fixed operations and management costs (€/kW): "))
            break
    elif show_char.lower() == 'n':
        # Get user inputs
        overnight_cost = float(input(f"Overnight construction costs (€/kW): "))
        fuel_cycle = float(input(f"Annual front and back-end fuel costs at 85% CF (€/kW): "))
        fixed_operations = float(input(f"Annual fixed operations and management costs (€/kW): "))
        break
    else:
        print("Invalid input, please try again.")

discount_rate = float(input("Discount rate: "))
escalation_rate = float(input("Escalation rate: "))
construction_time = int(input("Construction time in years: "))
utilization_hours = float(input("Power plant utilization hours in a year: "))

# Constants
capacity = 1000
lifetime = 60
kW_MW = 1000
calibration = utilization_hours / (7446 ** 2)

# Calculate CAPITAL
recovery_factor = (discount_rate * math.pow(1 + discount_rate, lifetime)) / (math.pow(1 + discount_rate, lifetime) - 1)
escalated_cost = sum((overnight_cost / construction_time) * (math.pow(1 + escalation_rate, t - 0.5)) for t in range(1, construction_time + 1))
investment_cost = sum((escalated_cost / construction_time) * (math.pow(1 + discount_rate, construction_time + 1 - t)) for t in range(1, construction_time + 1))
annual_capital_charge = investment_cost * kW_MW * recovery_factor
CAPITAL = annual_capital_charge / utilization_hours

# Calculate FOM
FOM = fixed_operations * kW_MW / utilization_hours

# Calculate VOM
VOM = fixed_operations * kW_MW * calibration / 9

# Calculate FUEL
FUEL = fuel_cycle * kW_MW * calibration

# Calculate DECOMMISSIONING
DECOMMISSIONING = ((overnight_cost * 0.15 * kW_MW * 0.01) / (math.pow(1.01, lifetime) - 1)) / utilization_hours

# Calculate LCOE
LCOE = CAPITAL + FOM + VOM + FUEL + DECOMMISSIONING
print(f"Total investment cost: €{investment_cost:.2f}/kW")
print(f"Levelized cost of electricity: €{CAPITAL:.2f}/MWh + €{FOM:.2f}/MWh + €{VOM:.2f}/MWh + €{FUEL:.2f}/MWh + €{DECOMMISSIONING:.2f}/MWh = €{LCOE:.2f}/MWh")
