import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # 1. تعريف الخدمات
    dynamodb = boto3.resource('dynamodb')
    sns = boto3.client('sns')
    
    # الجداول
    stock_table = dynamodb.Table('GhostCheckoutStock')
    orders_table = dynamodb.Table('GhostOrders')
    
    topic_arn = "arn:aws:sns:us-east-1:079485644301:SnapStockAlerts"
    
    try:
        # 2. تحديث المخزون (كودك القديم)
        response = stock_table.get_item(Key={'ProductID': 'Ghost_Ticket_001'})
        current_stock = int(response['Item']['StockCount'])
        new_stock = current_stock - 1
        
        stock_table.update_item(
            Key={'ProductID': 'Ghost_Ticket_001'},
            UpdateExpression="set StockCount = :s",
            ExpressionAttributeValues={':s': str(new_stock)}
        )
        
        # 3. تسجيل الطلب في جدول GhostOrders (الإضافة الجديدة)
        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        orders_table.put_item(
            Item={
                'orderId': order_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'SUCCESS',
                'remaining_stock': new_stock
            }
        )
        
        message = f"✅ SnapStock Success: Order {order_id} recorded. Remaining: {new_stock}"
        
        # 4. نظام التنبيه الذكي (كودك القديم)
        if new_stock <= 45:
            alert_msg = f"Alert Khuloud! SnapStock inventory is low. Only {new_stock} left."
            sns.publish(
                TopicArn=topic_arn,
                Message=alert_msg,
                Subject="⚠️ SnapStock Inventory Alert"
            )
            message += " (Alert Sent to Email!)"

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps(message)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f"Error: {str(e)}")
        }




