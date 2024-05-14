# Ebay Best Deals

![image](https://github.com/kirth123/ebaybestdeals/assets/88990184/d40b2a2f-dfe7-4063-a862-ad4b30d55e78)

This app scrapes the product details (i.e. price, number of items sold, etc) of all the kitchen appliances from the eBay's best deals page and saves them to a CSV file. The file is then uploaded to a AWS S3 bucket where AWS Glue can infer the relational schema of the file. I can run SQL queries using AWS Athena to figure out which products are the most popular and what characteristics they share.
