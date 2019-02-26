# CBBC-Outstanding-Distribution(depreciated as tencent API updated, the data are not real-time)

27-2-2019 update web scrapping HSI option data from HKEX to generate maximum option pain.

Using Python and Tencent API.

CBBC Outstanding Distribution is an important reference of the rise and fall of Hang Seng Index.

[![IMAGE ALT TEXT](http://img.youtube.com/vi/PoRSGyHuXJE/0.jpg)](https://www.youtube.com/watch?v=PoRSGyHuXJE "CBBC Distribution")

1. Get all warrant code from Futu Open API

2. Filter valid warrant using sina stock API( including CALL, PUT, BULL, BEAR)

3. Get the warrant outstanding distribution(街貨量)/ leverage(杠杆比率)/ price(價格) data of all valid warrant from Tencent API:

http://gu.qq.com/hk65093/qz

http://web.ifzq.gtimg.cn/appstock/app/HkWarrant/hkw?code=65093

4. Generate the distribution

Limitation: The warrant data from Tencent API may not be exactly real-time.
