default_earnings = [
                    {
                        "component_name": "Basic",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Percentage of CTC",
                            "value": 50
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": True,
                        "includes_epf_contribution": True,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": False,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": True
                    },
                    {
                        "component_name": "HRA",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Percentage of Basic",
                            "value": 50
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": True,
                        "includes_epf_contribution": False,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": False,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False

                    },
                    {
                        "component_name": "Fixed Allowance",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Remaining balance pf CTC",
                            "value": 0
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": True,
                        "includes_epf_contribution": True,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": True,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False
                    },
                    {
                        "component_name": "Conveyance Allowance",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Flat Amount",
                            "value": 50000
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": False,
                        "includes_epf_contribution": True,
                        "includes_esi_contribution": False,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": True,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False
                    },
                    {
                        "component_name": "Bonus",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Flat Amount",
                            "value": 0
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": False,
                        "includes_epf_contribution": False,
                        "includes_esi_contribution": False,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": "TDS",
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": False,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False,
                    },
                    {
                        "component_name": "Commission",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Flat Amount",
                            "value": 0
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": False,
                        "is_taxable": True,
                        "is_pro_rate_basis": False,
                        "includes_epf_contribution": False,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": False,
                        "pf_wage_less_than_15k": False,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion":False
                    },
                    {
                        "component_name": "Children Education Allowance",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Flat Amount",
                            "value": 0
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": True,
                        "includes_epf_contribution": True,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": True,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False
                    },
                    {
                        "component_name": "Transport Allowance",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Flat Amount",
                            "value": 1600
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": True,
                        "includes_epf_contribution": True,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": True,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False
                    },
                    {
                        "component_name": "Travelling Allowance",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Flat Amount",
                            "value": 1600
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": True,
                        "is_taxable": True,
                        "is_pro_rate_basis": True,
                        "includes_epf_contribution": True,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": True,
                        "pf_wage_less_than_15k": True,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False,
                    },
                    {
                        "component_name": "Overtime Allowance",
                        "component_type": "Fixed",
                        "calculation_type": {
                            "type": "Flat Amount",
                            "value": 1600
                        },
                        "is_active": True,
                        "is_part_of_employee_salary_structure": False,
                        "is_taxable": True,
                        "is_pro_rate_basis": False,
                        "includes_epf_contribution": False,
                        "includes_esi_contribution": True,
                        "is_included_in_payslip": True,
                        "tax_deduction_preference": None,
                        "is_scheduled_earning": False,
                        "pf_wage_less_than_15k": False,
                        "is_fbp_component": False,
                        "always_consider_epf_inclusion": False
                    }

]

