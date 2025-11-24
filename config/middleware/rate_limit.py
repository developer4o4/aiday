import time
from django.http import JsonResponse

# 1 soniyada nechta request ruxsat
RATE_LIMIT = 10

# Limit oshsa IP necha soniya bloklanadi
BLOCK_TIME = 60  # 60 sekund

# Xotirada saqlanadigan IP requestlar
ip_requests = {}

# Bloklangan IPlar
blocked_ips = {}

print(blocked_ips)
class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        ip = request.META.get("REMOTE_ADDR")
        now = time.time()

        # Agar IP blocklangan bo‘lsa
        if ip in blocked_ips:
            if blocked_ips[ip] > now:
                return JsonResponse(
                    {"error": "IP vaqtincha bloklangan. Juda ko‘p so‘rov yuborildi."},
                    status=429
                )
            else:
                blocked_ips.pop(ip)

        # IP bo‘lmasa yangisini ochamiz
        if ip not in ip_requests:
            ip_requests[ip] = []

        # Eski requestlarni tozalaymiz (1 sekund ichidagi requestlarni qoldiramiz)
        ip_requests[ip] = [t for t in ip_requests[ip] if now - t < 1]

        # Limitdan oshsa → block
        if len(ip_requests[ip]) >= RATE_LIMIT:
            blocked_ips[ip] = now + BLOCK_TIME
            return JsonResponse(
                {"error": "Rate limit: IP vaqtincha bloklandi"},
                status=429
            )

        # Yangi request vaqtini qo‘shamiz
        ip_requests[ip].append(now)

        response = self.get_response(request)
        return response
