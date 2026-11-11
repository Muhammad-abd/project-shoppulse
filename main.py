from test import reading_raw_logs, cleaning_raw_logs, analysis
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description="Project ShopPulse E-commerce Analytics Pipeline")
parser.add_argument("file", help="Path to transactions.txt")
parser.add_argument("-cat", "--category", type=str.capitalize, help="Filter by product category")
parser.add_argument("-amt", "--amount", type=float, help="Max amount threshold filter")
parser.add_argument("-t", "--top", type=int, default=5, help="Shows the top rows of the output")
parser.add_argument("-sd", "--start-date", help="Start date (YYYY-MM-DD)")
parser.add_argument("-ed", "--end-date", help="End date (YYYY-MM-DD)")
parser.add_argument("-st", "--start-time", help="Start time (HH:MM:SS)")
parser.add_argument("-et", "--end-time", help="End time (HH:MM:SS)")
args = parser.parse_args()

file_name = args.file
category_filter = args.category
amount_filter = args.amount
top_filter = args.top

start_date_filter = datetime.strptime(args.start_date, '%Y-%m-%d') if args.start_date else None
end_date_filter = datetime.strptime(args.end_date, '%Y-%m-%d') if args.end_date else None
start_time_filter = datetime.strptime(args.start_time, '%H:%M:%S').time() if args.start_time else None
end_time_filter = datetime.strptime(args.end_time, '%H:%M:%S').time() if args.end_time else None

def main():
    raw_log = reading_raw_logs(file_name)
    cleaned_log_in_list_form = cleaning_raw_logs(
        raw_log, category_filter, amount_filter, 
        start_date_filter, end_date_filter, 
        start_time_filter, end_time_filter
    )
    
    (
        total_revenue_per_product_category, 
        total_spendings_per_customer, 
        total_refund_per_customer, 
        status_count, 
        high_value_refunds,
        payment_method_tracker
    ) = analysis(cleaned_log_in_list_form, amount_filter)

    sorted_total_revenue_per_product_category = sorted(total_revenue_per_product_category.items(), key=lambda x: -x[1])[:top_filter]
    sorted_total_spendings_per_customer = sorted(total_spendings_per_customer.items(), key=lambda x: -x[1])[:top_filter]
    sorted_total_refund_per_customer = sorted(total_refund_per_customer.items(), key=lambda x: -x[1])[:top_filter]
    sorted_high_value_refunds = sorted(high_value_refunds.items(), key=lambda x: -x[1])[:top_filter]

    print("\nTOTAL REVENUE PER PRODUCT CATEGORY")
    print("-" * 50)
    for k, v in sorted_total_revenue_per_product_category:
        print(f" {k:<11} : ${v}")

    print("\nTOTAL SPENDINGS PER CUSTOMER")
    print("-" * 50)
    for k, v in sorted_total_spendings_per_customer:
        print(f" {k:<11} : ${v}")

    print("\nTOTAL REFUND PER CUSTOMER")
    print("-" * 50)
    for k, v in sorted_total_refund_per_customer:
        print(f" {k:<11} : ${v}")

    print("\nSTATUS COUNT")
    print("-" * 50)
    for k, v in status_count.items():
        print(f" {k:<11} : {v}")

    print("\nHIGH VALUE REFUNDS (>$500)")
    print("-" * 50)
    for k, v in sorted_high_value_refunds:
        print(f" {k:<11} : ${v}")
    print("-" * 50)

    print("\nPAYMENT GATEWAY REPORT")
    print("-" * 84)
    print(f"{'Payment Method':<16} | {'Total Orders':<14} | {'Successful':<14} | {'Failed/Other':<14} | {'Total Revenue':<12}")
    print("-" * 84)
    
    for k, v in payment_method_tracker.items():
        print(f"{k:<16} | {v['total_orders']:<14} | {v['successful_orders']:<14} | {v['failed/other_orders']:<14} | ${v['total_revenue']:>11.2f}")
    print("-" * 84)

if __name__ == "__main__":
    main()