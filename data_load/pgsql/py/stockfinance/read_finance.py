from pytdx.reader import HistoryFinancialReader
import pandas as pd

report_date_set =  ['20230930'] # 需要导入的报表日期
stockcode_prefix = ['00','30','60','68']
profit_import_flag = 1                          # ‘1’-导入利润表数据

# 利润表子程序

def profit_report_import(results,indexs,columns):
    for j in range (0,len(indexs)):
        p_stock_code = indexs[j]
        tmp_date = str(results.loc[indexs[j],columns[0]])
        p_report_date = tmp_date.split('.')[0]
        p_stockcode_prefix = p_stock_code[0:2]
        if p_report_date.isdigit() == False:
            continue
# filter    those not belong to A share
        if p_stockcode_prefix not in stockcode_prefix:
            continue

        p_FINONE_74_gross_income_operation = results.loc[indexs[j], columns[74]]
        p_FINONE_75_gross_cost_operation = results.loc[indexs[j], columns[75]]
        p_FINONE_76_operating_tax_addition = results.loc[indexs[j], columns[76]]
        p_FINONE_77_selling_expense = results.loc[indexs[j], columns[77]]
        p_FINONE_78_general_adm_expense = results.loc[indexs[j], columns[78]]
        p_FINONE_80_finance_expense = results.loc[indexs[j], columns[80]]
        p_FINONE_82_income_fair_value_change = results.loc[indexs[j], columns[82]]
        p_FINONE_83_income_invest_return = results.loc[indexs[j], columns[83]]
        p_FINONE_86_profit_operation = results.loc[indexs[j], columns[86]]
        p_FINONE_88_non_operating_income = results.loc[indexs[j], columns[88]]
        p_FINONE_89_non_operating_expense = results.loc[indexs[j], columns[89]]
        p_FINONE_92_profit_before_tax = results.loc[indexs[j], columns[92]]
        p_FINONE_93_income_tax = results.loc[indexs[j], columns[93]]
        p_FINONE_95_net_profit = results.loc[indexs[j], columns[95]]
        p_FINONE_96_net_profit_company_holder = results.loc[indexs[j], columns[96]]
        p_FINONE_97_minority_interest = results.loc[indexs[j], columns[97]]
        p_FINONE_300_other_income = results.loc[indexs[j], columns[300]]
        p_FINONE_301_return_of_assets_treatment = results.loc[indexs[j], columns[301]]
        p_FINONE_304_r_d_expense = results.loc[indexs[j], columns[304]]
        p_FINONE_305_interest_expense = results.loc[indexs[j], columns[305]]
        p_FINONE_306_interest_income = results.loc[indexs[j], columns[306]]
        p_FINONE_502_total_operation_income = results.loc[indexs[j], columns[502]]
        p_FINONE_509_interest_paid_out = results.loc[indexs[j], columns[509]]
        p_FINONE_510_service_fee_bonus = results.loc[indexs[j], columns[510]]
        p_FINONE_520_loss_assets_credit = results.loc[indexs[j], columns[517]]
        p_FINONE_521_loss_assets_impairment = results.loc[indexs[j], columns[81]]

        print(p_stock_code,p_report_date, p_FINONE_521_loss_assets_impairment,p_FINONE_301_return_of_assets_treatment,p_FINONE_520_loss_assets_credit)
 
file_name_prefix = 'F:\\pingan\\vipdoc\\cw\\gpcw' # 取决于个人软件的安装目录
file_name_postfix = '.zip'
for file_date in report_date_set:
    file_path = file_name_prefix + file_date + file_name_postfix
    print(file_path)

    pd.set_option('display.max_columns', None)
    results = HistoryFinancialReader().get_df(file_path)
    indexs = results._stat_axis.values.tolist()
    columns = results.columns.values.tolist()
    print(len(indexs),len(columns))

    if profit_import_flag == 1:
        print('PROFIT data importing on date:           ', file_date, ' in process ...')
        profit_report_import(results,indexs,columns)
        print('PROFIT data importing on date:           ', file_date, ' Done.')
