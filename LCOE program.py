## this is a tool to calculate LCOE of a nuclear power reactor (large and commercial)
## there are various options: default parameters, customized parameters, defualt design, default scenario/region/year

## sources:
##   [1] IEA projected costs of generation electricity 2020: https://www.iea.org/reports/projected-costs-of-generating-electricity-2020    
##   [2] IAEA Economic Evaluation of Alternative Nuclear Energy Systems (2014): https://www.iaea.org/publications/15192/economic-evaluation-of-alternative-nuclear-energy-systems
##   [3] IEA World Energy Outlook 2022: https://iea.blob.core.windows.net/assets/830fe099-5530-48f2-a7c1-11f35d510983/WorldEnergyOutlook2022.pdf#page=469
##   [4] IEA Net Zero by 2050, A Roadmap for the Global Energy Sector (2021): https://iea.blob.core.windows.net/assets/deebef5d-0c34-4539-9d0c-10b13d840027/NetZeroby2050-ARoadmapfortheGlobalEnergySector_CORR.pdf#page=202
##   [5] Capital cost estimation for advanced nuclear power plants (2022): https://www.sciencedirect.com/science/article/pii/S1364032121011473 
## for learning curve:
##   [6] OECD NEA Unlocking Reductions in the Construction Costs of Nuclear (2020): https://doi.org/10.1787/33ba86e1-en
##   [7] Lucid Catalyst con Energy Technology Institute: Nuclear Cost Divers Project (2020): https://www.lucidcatalyst.com/eti-nuclear-cost-drivers-full

## to be added: 
##   1. controls on inputs
##   2. MWh input
##   3. possibility to come back
##   4. Reactor() class formatting and possibility to edit for regional default parameters
##   5. total cost for reactor, learning curve
##   6. LTO
##   7. multiple option calculator (like same parameters but 3 different discount rate)
##   8. crete table and charts
##   9. other technology

# import libraries
import string
import copy
import math

## usefull function:

# function for check if an input is Y or N
# @output True if "Y" and False if "N"
def yes_no_input(input):
    control_input = str(input).upper()
    while control_input not in ["Y", "N"]:
        control_input = str(input("Input has to be Y or N, please re-enter it correctly: ")).upper()
    if control_input == "Y":
        return True
    else:
        return False


# function for print a list with numbered and alphabetic or input index
# @output is string or it print directly inside the function based on the @input string [print by default]
def print_list(list, index=0, sep=". ", double_index = False, input_index = [""], string = False):
    if(input_index[index]==""):
        second_index=[""]*26
        if(string):
            output = ""
            if(double_index):
                i = 0
                for letter in string.ascii_lowercase:
                    second_index[i] = f"({letter})"
                    i+=1
            while(index < len(list)):
              output = output + f"{index+1}{second_index[index]}{sep}{list[index]}\n"
              index+=1
            return output + f"\n"
        else:
            if(double_index):
                i = 0
                for letter in string.ascii_lowercase:
                    second_index[i] = f"({letter})"
                    i+=1
            while(index < len(list)):
              print(f"{index+1}{second_index[index]}{sep}{list[index]}")
              index+=1
            print("")
    else:
        if(string):
            output = ""
            while(index < len(list)):
              output = output + f"{input_index[index]}{sep}{list[index]}\n"
              index+=1
            return output + f"\n"
        else:
            while(index < len(list)):
              print(f"{input_index[index]}{sep}{list[index]}")
              index+=1
            print("")

## real program:

# formula for calculate Levelized Cost Of Electricity [$/MWh]
# formulas based on [2]
# with the exception of Fuel and O&M costs for which various other data and prices would be needed 
# so an approximation has been used
# @output princt LCOE breakdown or just LCOE based on the @input only_result [default = False]
def LCOE_calculator(capacity, lifetime, utilization_hours, construction_time, discount_rate, escalation_rate, overnight_costs, fuel_cycle_costs, FOM_costs, VOM_costs, only_result = False): # O_M_costs
    
    # useful costants
    kW_MW = 1000 # convertion kW <-> MW

    # Calculate CAPITAL
    recovery_factor = (discount_rate * math.pow(1 + discount_rate, lifetime)) / (math.pow(1 + discount_rate, lifetime) - 1)
    escalated_cost = sum((overnight_costs / construction_time) * (math.pow(1 + escalation_rate, t - 0.5)) for t in range(1, construction_time + 1))
    investment_cost = sum((escalated_cost / construction_time) * (math.pow(1 + discount_rate, construction_time + 1 - t)) for t in range(1, construction_time + 1))
    annual_capital_charge = investment_cost * kW_MW * recovery_factor
    CAPITAL = Parameter(name = "Capital", unit_of_measurement = "$/MWh", value = round(annual_capital_charge / utilization_hours, 2))

    # Calculate FOM
    FOM = Parameter(name = "Fixed Operation and Maintenance", unit_of_measurement = "$/MWh", value = round(FOM_costs * kW_MW / utilization_hours, 2))

    # Calculate VOM
    VOM = Parameter(name = "Variable Operation and Maintenance", unit_of_measurement = "$/MWh", value = round(VOM_costs * kW_MW / utilization_hours, 2))

    # Calculate FUEL
    FUEL = Parameter(name = "Fuel", unit_of_measurement = "$/MWh", value = round(fuel_cycle_costs * kW_MW / utilization_hours, 2))

    # Calculate DECOMMISSIONING, interest of decommissioning fund is assumed to be 0.01 
    DECOMMISSIONING = Parameter(name = "Decommissioning", unit_of_measurement = "$/MWh", value = round(((overnight_costs * 0.15 * kW_MW * 0.01) / (math.pow(1.01, lifetime) - 1)) / utilization_hours, 2))

    # Calculate LCOE
    LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = round(CAPITAL.value + FOM.value + VOM.value + FUEL.value + DECOMMISSIONING.value, 2))
    # print result
    list_scomposed = [CAPITAL, FOM, VOM, FUEL, DECOMMISSIONING]
    print(f"{LCOE.print_value()}")
    if(not only_result):
        print(f"\nCosts breakdown by category:")
        [print(f"{value.print_value()}") for value in list_scomposed]
        print(f"\nCosts breakdown in percentage:")
        [print(f"{value.name}: {(value.value/LCOE.value*100):.2f} %") for value in list_scomposed]


# class for name, unit of measurement and value of parameters
class Parameter:
    def __init__(self, name, unit_of_measurement, value):
        self.name = name
        self.unit_of_measurement = unit_of_measurement
        self.value = value   
    
    def edit_value(self, new_value):
        if (type(self.value) is int):
            self.value = round(new_value)
        else: self.value = new_value
    
    # functions for print the parameter with 3 different format
    def print_name(self):
        if(self.unit_of_measurement == ""):
            return f"{self.name}"
        else:
            return f"{self.name} [{self.unit_of_measurement}]"
    def print_value(self):
        if(self.unit_of_measurement == ""):
            return f"{self.name}: {self.value}"
        else:
            return f"{self.name}: {self.value} [{self.unit_of_measurement}]"
    
    def print_only_value(self):
        if(self.unit_of_measurement == ""):
            return f"{self.value}"
        else:
            return f"{self.value} [{self.unit_of_measurement}]"
    

# create object Reactor
# all @var are object of the Parameter class
# has method for edit parameters, calculate LCOE, use default design or scenario/region/year
class Reactor:
    def __init__(self, capacity = Parameter(name = "Capacity", unit_of_measurement = "MW", value = int(1000)), lifetime = Parameter(name = "Lifetime", unit_of_measurement = "year", value = int(60)), 
                 utilization_hours = Parameter(name = "Utilization Hours", unit_of_measurement = "h", value = int(7884)), construction_time = Parameter(name = "Construction Time", unit_of_measurement = "year", value = int(7)), 
                 discount_rate = Parameter(name = "Discout Rate ", unit_of_measurement = "", value = float(0.07)), escalation_rate = Parameter(name = "Escalation Rate ", unit_of_measurement = "", value = float(0.01)),
                 overnight_costs = Parameter(name = "Overnight Construction Costs", unit_of_measurement = "$/kW", value = int(4000)), fuel_cycle_costs = Parameter(name = "Fuel Cycle Costs", unit_of_measurement = "$/kW y", value = float(70)), 
                 FOM_costs = Parameter(name = "Fix Operation and Maintainance costs", unit_of_measurement = "$/kW y", value = float(112)), VOM_costs = Parameter(name = "Variable Operation and Maintainance costs", unit_of_measurement = "$/kW y", value = float(13))):
                 # O_M_costs = Parameter(name ="Operation and Maintenance costs", unit_of_measurement = "$/kW", value = 125)
        self.capacity = copy.deepcopy(capacity)
        self.lifetime = copy.deepcopy(lifetime)
        self.utilization_hours = copy.deepcopy(utilization_hours)
        self.construction_time = copy.deepcopy(construction_time)
        self.discount_rate = copy.deepcopy(discount_rate)
        self.escalation_rate = copy.deepcopy(escalation_rate)
        self.overnight_costs = copy.deepcopy(overnight_costs)
        self.fuel_cycle_costs = copy.deepcopy(fuel_cycle_costs)
        self.FOM_costs = copy.deepcopy(FOM_costs)
        self.VOM_costs = copy.deepcopy(VOM_costs)
        # self.O_M_costs = copy.deepcopy(O_M_costs)
        self.list_value = [value for key, value in self.__dict__.items()]
        self.list_print = [value.print_value() for value in self.list_value] # parameters formatting for print the list
        self.choose_CF_UH = 0
        self.edit_total_O_M_done = False
  
    # @input if edit_all == True -> edit all parameters
    def edit_parameter(self, edit_all = False):
        list_name = [value.print_name() for value in self.list_value] # name of parameters
        if(edit_all): # edit all parameters
            for parameter in range(0,len(list_name)):
                if(parameter == 2): # edit CF or UH
                    self.utilization_hours.edit_value(self.ask_CF_UH())
                    print(f"Value updated:\n{self.list_value[parameter].print_value()}\n")
                    continue
                elif(parameter == 7): # edit Fuel costs may need a calibration
                    self.fuel_cycle_costs.edit_value(float(input(f"Digit the value for {list_name[parameter]}: ")))
                    calibration = self.calibration("Fuel")
                    self.fuel_cycle_costs.edit_value(round(self.fuel_cycle_costs.value*calibration))
                    print(f"Value updated:\n{self.list_value[parameter].print_value()}\n")
                    continue
                elif(parameter == 8): # edit FOM or O_M
                    edit_total = yes_no_input(input(f"Do you want to edit total Operation and Maintenance? [y/n]: "))
                    if(edit_total):
                        self.O_M_breakdown(O_M_costs = float(input(f"Digit the value for total Operation and Maintenance [$/kW y]: ")))
                        print(f"Values updated:\n{self.list_value[8].print_value()}\n{self.list_value[9].print_value()}\n")
                        break
                elif(parameter == 9): 
                    self.VOM_costs.edit_value(float(input(f"Digit the value for Variable Operation and Maintainance costs [$/kW y]: ")))
                    calibration = self.calibration("VOM")
                    self.VOM_costs.edit_value(round(self.VOM_costs.value*calibration))
                    print(f"Value updated:\n{self.list_value[parameter].print_value()}\n")
                    break
                self.list_value[parameter].edit_value(float(input(f"Digit the new value for {list_name[parameter]}: ")))
                print(f"Value updated:\n{self.list_value[parameter].print_value()}\n")
            pass
        else: # edit a single parameter
            end = False
            while(not end): 
                print(f"\nWhat parameter do you want to edit?")
                print_list(self.list_print) # print current parameters
                print(f"FOM and VOM can be edited individually or you can provide the total costs of Operation and Maintenance and there will be an approximation of the breakdown (the approximation is godd for CF>=80%)")
                parameter = int(input(f"\nDigit the associated number and press Enter: "))
                if(parameter in [9,10]): # edit FOM, VOM or O_M
                    if(not self.edit_total_O_M_done):
                        edit_total = yes_no_input(input(f"Do you want to edit total Operation and Maintenance? [y/n]: "))
                        self.edit_total_O_M_done = True
                        if(edit_total):
                            self.O_M_breakdown(O_M_costs = float(input(f"Digit the value for total Operation and Maintenance [$/kW y]: ")))
                    elif(parameter == 9):
                        self.FOM_costs.edit_value(float(input(f"Digit the value for Fix Operation and Maintainance costs [$/kW y]: ")))
                    elif(parameter == 10): 
                        self.VOM_costs.edit_value(float(input(f"Digit the value for Variable Operation and Maintainance costs [$/kW y]: ")))
                        calibration = self.calibration("VOM")
                        self.VOM_costs.edit_value(round(self.VOM_costs.value*calibration))
                    print(f"Values updated:\n{self.list_value[8].print_value()}\n{self.list_value[9].print_value()}\n")
                elif(parameter == 3): # edit CF or UH
                    self.utilization_hours.edit_value(self.ask_CF_UH())
                    print(f"Value updated:\n{self.list_value[parameter - 1].print_value()}\n")
                elif(parameter == 8): # edit Fuel costs may need a calibration
                    self.fuel_cycle_costs.edit_value(float(input(f"Digit the value for {list_name[parameter - 1]}: ")))
                    calibration = self.calibration("Fuel")
                    self.fuel_cycle_costs.edit_value(round(self.fuel_cycle_costs.value*calibration))
                    print(f"Value updated:\n{self.list_value[parameter - 1].print_value()}\n")
                else:
                    self.list_value[parameter - 1].edit_value(float(input(f"Digit the new value for {list_name[parameter - 1]}: ")))
                    print(f"Value updated:\n{self.list_value[parameter - 1].print_value()}\n")
                self.list_print = [value.print_value() for value in self.list_value] # update list for print update
                end = not yes_no_input(input(f"Do you want to edit more parameters? [y/n]: "))
        return Reactor(*self.list_value)
    
    # function dedicated to ask Capacity Factor or Utilization Hours
    # @return Utilization Hours
    def ask_CF_UH(self):
        if(self.choose_CF_UH == 0): # do not ask every time and preserv user choice
            print(f"Do you want to enter Capacity Factor or Utilization Hours?: ")
            print_list(["Capacity Factor","Utilization Hours"])
            self.choose_CF_UH = int(input(f"Digit the associated number and press Enter: "))
        if(self.choose_CF_UH == 1):
            CF = float(input(f"Digit the value for Capacity Factor: "))
            alert = (CF>1)
            while(alert):
                CF = float(input(f"Attention you entered a Capacity Factor > 1, please re-enter it correctly: "))
                alert = (CF>1)
            utilization_hours = round(CF*365*24)
        else:
            utilization_hours = int(input(f"Digit the value for Utilization Hours: "))
        return utilization_hours
    
    # function for when the CF or UH influence a parameter
    # @input make_decision for directly choose "skip" [decision = 3]
    # @return the recalibraction factor
    def calibration(self, parameter, make_decision = True):
        if(make_decision):
            print("\nThe Capacity Factor and so the value of Utilization Hours influence "+parameter+", now it's: "+self.utilization_hours.print_only_value()+", do you want to:")
            print_list(["edit the UH or CF", "enter for which UH or CF the inserted "+parameter+" is calculated and have it recalculated automatically according to the current CF", "skip"])
            decision = int(input(f"Digit the associated number and press Enter: "))
        else:
            decision = 3
        calibration = 1
        if(decision == 1):
            self.utilization_hours.edit_value(self.ask_CF_UH())
            print(f"Value updated:\n{self.utilization_hours.print_value()}\n")
        elif(decision == 2):
            UH_used = self.ask_CF_UH()
            calibration = self.utilization_hours.value / UH_used
        return calibration
    
    # function for breakdown O&M costs in FOM and VOM
    # @input O&M costs value
    # @input calibration_decision for automatic calculation of breakdown without other input
    # paramteres are uptdated inside the function
    def O_M_breakdown(self, O_M_costs, calibration_decision = True):
        calibration = self.calibration("O&M", make_decision = calibration_decision)
        # at CF >= 80% VOM is approsively 1/9 of FOM
        self.FOM_costs.edit_value(round(O_M_costs/10*9))
        self.VOM_costs.edit_value(round(O_M_costs/10*calibration))
        
    #def convert_MWh_kW(self, value_MWh): ## to be added
    #    pass
    
    # function for calculate and print LCOE with current parameters
    def LCOE_calculator(self):
        LCOE_calculator(capacity = self.capacity.value, lifetime = round(self.lifetime.value), utilization_hours = self.utilization_hours.value, construction_time = round(self.construction_time.value), discount_rate = self.discount_rate.value, escalation_rate = self.escalation_rate.value, overnight_costs = self.overnight_costs.value, fuel_cycle_costs = self.fuel_cycle_costs.value, FOM_costs = self.FOM_costs.value, VOM_costs = self.VOM_costs.value)
    
    def default_design(self): # use default design
        self.design_list = ["EPR (France)", "ABWR (Japan)", "APR1400 (Korea)", "AP1000 (United States)", "VVER (Russia)", "CAP1400 (China)", "PHWR (India)"]
        print(f"Select the design: ")
        print_list(self.design_list)
        return Reactor_Design(design_name = self.design_list[int(input(f"Digit the associated number and press Enter: "))-1])
    
    def default_region_LCOE(self): # use default region with LCOE already calculated by IEA
        self.scenario_list = ["Net Zero by 2050", "Announced Pledges", "Stated Policies", "Multi-Scenario"]
        self.region_list = ["United States", "European Union", "China", "India", "Multi-Region"]
        self.year_list = ["2021", "2030", "2050", "Multi-Year"]
        print(f"\nSelect the scenario: ")
        print_list(self.scenario_list)
        scenario = self.scenario_list[int(input(f"Digit the associated number and press Enter: "))-1]
        print(f"\nSelect the region: ")
        print_list(self.region_list)
        region = self.region_list[int(input(f"Digit the associated number and press Enter: "))-1]
        print(f"\nSelect the year: ")
        print_list(self.year_list)
        year = self.year_list[int(input(f"Digit the associated number and press Enter: "))-1]
        print("")
        return Reactor_Region_LCOE(scenario_name = scenario, region_name = region, year_name = year)
    
    def __repr__(self): # return a string with the reactor parameters in their value format
        return print_list(self.list_print, input_index = ["●"]*len(self.list_print), sep = " " ,string = True)


# sub class of Reactor for use default design
# data from [1] Capacity Factor is set to 85% because data are provided whit this CF
# @var design_name (string) the name of the design
class Reactor_Design(Reactor):
    def __init__(self, design_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.design_name = design_name
        self.assign_design()
    
    # assign the values of the selected design
    # values have been previously converted in $/kW 
    def assign_design(self):
        if(self.design_name == "EPR (France)"):
            self.capacity.edit_value(1650)
            self.utilization_hours.edit_value(round(0.85*365*24))
            self.overnight_costs.edit_value(4013)
            self.fuel_cycle_costs.edit_value(70)
            self.O_M_breakdown(O_M_costs = 96, calibration_decision = False)
        elif(self.design_name == "ABWR (Japan)"):
            self.capacity.edit_value(1152)
            self.utilization_hours.edit_value(round(0.85*365*24))
            self.overnight_costs.edit_value(3963)
            self.fuel_cycle_costs.edit_value(103)
            self.O_M_breakdown(O_M_costs = 173, calibration_decision = False)
        elif(self.design_name == "APR1400 (Korea)"):
            self.capacity.edit_value(1400)
            self.utilization_hours.edit_value(round(0.85*365*24))
            self.overnight_costs.edit_value(2157)
            self.fuel_cycle_costs.edit_value(70)
            self.O_M_breakdown(O_M_costs = 124, calibration_decision = False)
        elif(self.design_name == "AP1000 (United States)"):
            self.capacity.edit_value(1100)
            self.utilization_hours.edit_value(round(0.85*365*24))
            self.overnight_costs.edit_value(4250)
            self.fuel_cycle_costs.edit_value(70)
            self.O_M_breakdown(O_M_costs = 77, calibration_decision = False)
        elif(self.design_name == "VVER (Russia)"):
            self.capacity.edit_value(1112)
            self.utilization_hours.edit_value(round(0.85*365*24))
            self.overnight_costs.edit_value(2271)
            self.fuel_cycle_costs.edit_value(37)
            self.O_M_breakdown(O_M_costs = 68, calibration_decision = False)
        elif(self.design_name == "CAP1000 (China)"):
            self.capacity.edit_value(950)
            self.utilization_hours.edit_value(round(0.85*365*24))
            self.overnight_costs.edit_value(2500)
            self.fuel_cycle_costs.edit_value(75)
            self.O_M_breakdown(O_M_costs = 177, calibration_decision = False)
        elif(self.design_name == "PHWR (India)"):
            self.capacity.edit_value(950)
            self.utilization_hours.edit_value(round(0.85*365*24))
            self.overnight_costs.edit_value(2778)
            self.fuel_cycle_costs.edit_value(70)
            self.O_M_breakdown(O_M_costs = 160, calibration_decision = False)
        self.list_print = [value.print_value() for value in self.list_value] # update list for print update
    
    def __repr__(self): # return a string with the reactor parameters in their value format and the design name
        return f"Design: {self.design_name}\nParameters:\n"+print_list(self.list_print, input_index = ["●"]*len(self.list_print), sep = " " ,string = True)
 

## to be added
# sub class of Reactor for use default scenario/region/year
# data from [3]
# @var regionn_name (string) the name of the region
"""
class Reactor_Region(Reactor):
    def __init__(self, scenario_name, region_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scenario_name = scenario_name
        self.region_name = region_name
        self.assign_region()
    
    # assign the values of the selected region
    def assign_region(self):
        pass
"""


# sub class of Reactor for use default scenario/region/year
# data from [3] but using the LCOE already calulated by IEA
# @var regionn_name (string) the name of the region
class Reactor_Region_LCOE():
    def __init__(self, scenario_name, region_name, year_name):
        self.scenario_name = scenario_name
        self.region_name = region_name
        self.year_name = year_name
        self.assign_region()
        self.list_value = [value for key, value in self.__dict__.items()]
        self.list_print = [value.print_value() for value in self.list_value[3:]] # parameters formatting for print the list
        
    # assign the values of the selected region
    def assign_region(self):
        # IEA assume for nuclear power a standard WACC of 7‐8% based on the stage of economic development
        # information from the [4] are used for attribute 0.08 to US and EU, 0.07 to CN and IN
        if(self.scenario_name == "Net Zero by 2050"):
            if(self.year_name == "2021"):
                if(self.region_name == "United States"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 5000)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 100)
                elif(self.region_name == "European Union"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 6600)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 140)
                elif(self.region_name == "China"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.85)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
                elif(self.region_name == "India"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.70)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 75)
            elif(self.year_name == "2030"):
                if(self.region_name == "United States"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 100)
                elif(self.region_name == "European Union"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 5100)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 115)
                elif(self.region_name == "China"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
                elif(self.region_name == "India"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.85)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
            elif(self.year_name == "2050"):
                if(self.region_name == "United States"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.85)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 100)
                elif(self.region_name == "European Union"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.70)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 115)
                elif(self.region_name == "China"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.70)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
                elif(self.region_name == "India"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
        elif(self.scenario_name == "Announced Pledges"):
            if(self.year_name == "2021"):
                if(self.region_name == "United States"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 5000)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 100)
                elif(self.region_name == "European Union"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 6600)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 140)
                elif(self.region_name == "China"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.85)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
                elif(self.region_name == "India"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.75)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 70)
            if(self.year_name == "2030"):
                if(self.region_name == "United States"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 100)
                elif(self.region_name == "European Union"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 5100)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 115)
                elif(self.region_name == "China"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
                elif(self.region_name == "India"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.85)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
            if(self.year_name == "2050"):
                if(self.region_name == "United States"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 100)
                elif(self.region_name == "European Union"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.70)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 115)
                elif(self.region_name == "China"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 60)
                elif(self.region_name == "India"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
        elif(self.scenario_name == "Stated Policies"):
            if(self.year_name == "2021"):
                if(self.region_name == "United States"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 5000)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 105)
                    # IEA report has a discrepancy LCOE in the other scenarios is 100 with the same parameters
                elif(self.region_name == "European Union"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 6600)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 140)
                elif(self.region_name == "China"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
                elif(self.region_name == "India"):
                    self.discount_rate = Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.75)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 75)
                    # IEA report has a discrepancy LCOE in the other scenarios is 70 with the same parameters
            if(self.year_name == "2030"):
                if(self.region_name == "United States"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 100)
                elif(self.region_name == "European Union"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 5100)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 120)
                    # IEA report has a discrepancy LCOE in the other scenarios is 115 with the same parameters
                elif(self.region_name == "China"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
                elif(self.region_name == "India"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.85)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)
            if(self.year_name == "2050"):
                if(self.region_name == "United States"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 95)
                    # IEA report has a discrepancy LCOE in the Announced Pledges Scenario is 100 with the same parameters
                elif(self.region_name == "European Union"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.08)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 4500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 35)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 105)
                elif(self.region_name == "China"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2500)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.80)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 25)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 60)
                elif(self.region_name == "India"):
                    self.discount_rate=Parameter(name="Discount Rate ",unit_of_measurement="", value=0.07)
                    self.overnight_costs = Parameter(name = "Overnight Costs", unit_of_measurement = "$/kW", value = 2800)
                    self.capacity_factor = Parameter(name = "Capacity Factor", unit_of_measurement = "", value = 0.90)       
                    self.Fuel_O_M = Parameter(name = "Fuel and Operation and Maintainance Costs", unit_of_measurement = "$/MWh", value = 30)
                    self.LCOE = Parameter(name = "Levelized Cost Of Electricity", unit_of_measurement = "$/MWh", value = 65)

    def __repr__(self): # return a string with the reactor parameters in their value format and the scenario/region/year names
        if(self.scenario_name == "Multi-Scenario"):
            multi_scenario = ""
            for scenario in ["Net Zero by 2050", "Announced Pledges", "Stated Policies"]:
                temp_reactor = Reactor_Region_LCOE(scenario_name = scenario, region_name = self.region_name, year_name = self.year_name)
                multi_scenario = multi_scenario + str(temp_reactor)
            return multi_scenario
        elif(self.region_name == "Multi-Region"):
            multi_region = ""
            for region in ["United States", "European Union", "China", "India"]:
                temp_reactor = Reactor_Region_LCOE(scenario_name = self.scenario_name, region_name = region, year_name = self.year_name)
                multi_region = multi_region + str(temp_reactor)
            return multi_region
        elif(self.year_name == "Multi-Year"):
            multi_year = ""
            for year in ["2021", "2030", "2050"]:
                temp_reactor = Reactor_Region_LCOE(scenario_name = self.scenario_name, region_name = self.region_name, year_name = year)
                multi_year = multi_year + str(temp_reactor)
            return multi_year
        else:
            return f"Scenario: {self.scenario_name}\nRegion: {self.region_name}\nYear: {self.year_name}\nParameters:\n"+print_list(self.list_print, input_index = ["●"]*len(self.list_print), sep = " " ,string = True)


# main function for the user interaction
def main():
    
    #welcome
    print("Welcome on nuclear LCOE calculator !")
    new_reactor = Reactor() # create dafault reactor
    print("\nDefault parameters:")
    print(new_reactor) # print  default parameters
    
    # choose the customization
    what_to_do = ["Use all default parameters", "Edit some parameters", "Customize all the parameters", 
                  "Start from a default design (value from IEA Projected Costs of Generating Electricity 2020) (you will still be able to edit the parameters)", 
                  "Use default Scenario, Geographic Region and Year (parameters and LCOE already calculated by IEA in World Energy Outlook 2022)"]
    print("Select what to do:")
    print_list(what_to_do)
    customization = int(input(f"Digit the associated number and press Enter: "))
    print("")
    # editing of parameters
    edit = False
    if(customization == 3):
        new_reactor = new_reactor.edit_parameter(edit_all = True)
    elif(customization == 4):
        new_reactor = new_reactor.default_design()
        edit = yes_no_input(input(f"Do you want to edit some parameters? [y/n]: "))
    elif(customization == 5):
        new_reactor = new_reactor.default_region_LCOE()
    if(customization == 2 or edit):
        new_reactor = new_reactor.edit_parameter() 
    if(not customization == 5):
        # print final parameters and LCOE
        what_customization = ["default reactor", "customizated reactor", "totally customizated reactor", 
                              "{new_reactor.design_name} design", "{new_reactor.region_name} region"]
        print(f"\nFinal values for {what_customization[customization-1]}: ")
        print(new_reactor)
        new_reactor.LCOE_calculator()
    else:
        print(new_reactor)
    
main()
