from datetime import datetime, timedelta

def reading_raw_logs(file_name):
    try:
        with open(file_name, 'r') as file:
            for line in file:
                if not line.strip():
                    continue
                yield line
    except IOError:
        return

def cleaning_raw_logs(raw_log, category_filter=None, 
                      amount_filter=None, start_date_filter=None,
                      end_date_filter=None, start_time_filter=None,
                      end_time_filter=None):
    for log in raw_log:
        if '|' not in log:
            continue

        log_in_list_form = [i.strip() for i in log.split('|')]
        if len(log_in_list_form) != 7:
            continue
            
        try:
            amount = float(log_in_list_form[4])
        except ValueError:
            continue

        if category_filter and category_filter.lower() != log_in_list_form[3].lower():
            continue

        if amount_filter is not None and amount > amount_filter:
            continue

        try:
            date_time = log_in_list_form[1]
            date_time_in_list_form = date_time.split()
            date_string = date_time_in_list_form[0].strip()
            time_string = date_time_in_list_form[1].strip()
            date = datetime.strptime(date_string, '%Y-%m-%d')
            time = datetime.strptime(time_string, '%H:%M:%S').time()
        except (ValueError, IndexError):
            continue

        if start_date_filter and date < start_date_filter:
            continue

        if end_date_filter and date > end_date_filter:
            continue

        if start_time_filter and time < start_time_filter:
            continue

        if end_time_filter and time > end_time_filter:
            continue

        yield log_in_list_form

def analysis(cleaned_log_in_list_form, amount_filter=None):
    total_revenue_per_product_category = {}
    total_spendings_per_customer = {}
    total_refund_per_customer = {}
    status_count = {}
    high_value_refunds = {}
    payment_method_tracker = {}
    hourly_order_revenue_analysis = {}

    for log in cleaned_log_in_list_form:
        category = log[3].capitalize()
        status = log[6].upper()
        customer = log[2]
        order_id = log[0]
        payment_type = log[5].upper()
        date_time = log[1]
        date_time_in_list_form = date_time.split()
        time_string = date_time_in_list_form[1].strip()
        time = datetime.strptime(time_string, '%H:%M:%S').time()
        #diff_time = timedelta(hours=0, minutes=59, seconds=59) 
        round_off_time_only_hours = time.replace(minute=0, second=0)
        #time_diff = time - round_off_time_only_hours
        time_block = round_off_time_only_hours.strftime("%H:%M")
        
        try:
            amount = float(log[4])
        except ValueError:
            continue

        #hourly_order_review_analysis
        #if time_diff <= diff_time:
        hourly_order_revenue_analysis.setdefault(time_block, {'total_orders':0, 'total_revenue': 0.0}) 
        hourly_order_revenue_analysis[time_block]['total_orders'] = hourly_order_revenue_analysis[time_block].get('total_orders',0) + 1

        
            



        # 0. Payment getway tracker
        payment_method_tracker.setdefault(payment_type, {'total_orders': 0, 'successful_orders': 0, 
                                                   'failed/other_orders': 0, 'total_revenue': 0.0})

        # 0.1 total_orders_count
        payment_method_tracker[payment_type]['total_orders'] = payment_method_tracker[payment_type].get('total_orders',0) + 1

        # 1. Category Revenue Leaderboard (COMPLETED orders only)
        if status == "COMPLETED":
            total_revenue_per_product_category.setdefault(category, 0.0)
            total_revenue_per_product_category[category] = round(total_revenue_per_product_category[category] + amount, 2)

        # 0.2 successful_transactions_count_per_payment_category_type
            payment_method_tracker[payment_type]['successful_orders'] = payment_method_tracker[payment_type].get('successful_orders',0) + 1


            # 2. Top Spending Customers (COMPLETED orders)
            total_spendings_per_customer.setdefault(customer, 0.0)
            total_spendings_per_customer[customer] = round(total_spendings_per_customer[customer] + amount, 2)

            #0.4 total_revenue_per_payment_category
            payment_method_tracker[payment_type]['total_revenue'] = round((payment_method_tracker[payment_type].get('total_revenue',0) + amount),2)

            hourly_order_revenue_analysis[time_block]['total_revenue'] = hourly_order_revenue_analysis[time_block].get('total_revenue',0) + amount

        else:
            #0.3 failed_and_other_status_type_count_per_payment_category_type
            payment_method_tracker[payment_type]['failed/other_orders'] = payment_method_tracker[payment_type].get('failed/other_orders',0) + 1
            

        # 3. Total Refund Per Customer (REFUNDED orders)
        if status == "REFUNDED":
            total_refund_per_customer.setdefault(customer, 0.0)
            total_refund_per_customer[customer] = round(total_refund_per_customer[customer] + amount, 2)

            # 4. High-Value Refunds (Status == REFUNDED and amount > $500.00)
            if amount > 500.00:
                high_value_refunds[order_id] = amount

        # 5. Transaction Status Count
        status_count.setdefault(status, 0)
        status_count[status] += 1

        
    return (
        total_revenue_per_product_category, 
        total_spendings_per_customer, 
        total_refund_per_customer, 
        status_count, 
        high_value_refunds,
        payment_method_tracker,
        hourly_order_revenue_analysis
    )