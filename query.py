BULK_OPERATION_RUN_QUERY = '''
mutation bulk_product_query($subquery: String!)  {
  bulkOperationRunQuery(
    query: $subquery
  ) {
    bulkOperation {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
'''
GET_ALL_ORDERS_QUERY = """
{
  orders {
    edges {
      node {
        __typename
        id
        createdAt
        processedAt
        updatedAt
        test
        customerLocale
        customer {
            id
        }
        app {
            id
        }
        customerJourneySummary {
            daysToConversion
            customerOrderIndex
            momentsCount
            ready
            firstVisit {
                id
                landingPage
                occurredAt
                referrerUrl
                source
                sourceType
                utmParameters {
                    campaign
                    content
                    medium
                    source
                    term
                }
                occurredAt
            }
            
             lastVisit {
                id
                landingPage
                occurredAt
                referrerUrl
                source
                sourceType
                utmParameters {
                    campaign
                    content
                    medium
                    source
                    term
                }
                occurredAt
            }
            moments (first: 20) {
                edges {
                    node {
                        __typename
                        occurredAt

                    }
                }
            }
        }
        totalPriceSet {
          shopMoney {
            amount
          }
        }
        subtotalPriceSet {
          shopMoney {
            amount
          } 
        }
        taxLines {
          rate
          priceSet {
            shopMoney {
              amount
            }
          }
        }
        totalDiscountsSet {
          shopMoney {
            amount
          }
        }
        totalRefundedSet {
          shopMoney {
            amount
          }
        }
        fullyPaid
        subtotalLineItemsQuantity
        cancelledAt
        cancelReason
        closed
        closedAt
        presentmentCurrencyCode
        shippingAddress {
            countryCodeV2
            city
            latitude
            longitude
            provinceCode
        }
        shippingLine {
            id
            title
            source
            deliveryCategory
            carrierIdentifier
            discountedPriceSet {
                shopMoney {
                    amount
                }
            }
            originalPriceSet {
                shopMoney {
                    amount
                }
            }
            taxLines {
                rate
                priceSet {
                    shopMoney {
                        amount
                    }
                }
            }
        }
        discountApplications(first: 10) {
          edges {
            node {
              __typename  
              allocationMethod
              index
              targetSelection
              targetType
              value {
                ... on MoneyV2 {
                  amount
                  currencyCode
                }
                ... on PricingPercentageValue {
                  percentage
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
GET_ALL_CUSTOMERS_QUERY = """
query customers {
        customers {
            edges {
                node {
                    __typename
                    id
                    firstName
                    lastName
                    email
                    phone
                    locale
                    state
                    createdAt
                    updatedAt
                    taxExempt
                    lifetimeDuration
                    statistics {
                        predictedSpendTier
                    }
                    addresses {
                        id
                        address1
                        address2
                        city
                        company
                        countryCodeV2
                        latitude
                        longitude
                        province
                        provinceCode
                        timeZone
                        zip
                    }
                    emailMarketingConsent {
                        consentUpdatedAt
                        marketingState
                        marketingOptInLevel
                    }
                    smsMarketingConsent {
                        consentUpdatedAt
                        marketingState
                        marketingOptInLevel
                    }
                    lastOrder {
                        id
                    }
                    numberOfOrders
                    amountSpent {
                        currencyCode
                        amount
                    }
                }
            }
        }
}
"""
GET_ALL_PRODUCTS_QUERY = """{
      products {
        edges {
          node {
            id
            __typename
            createdAt
            updatedAt
            title
            productType
            totalInventory
            publishedAt
            mediaCount
            options {
              id
              name
              position
              values
            }
            priceRangeV2 {
              minVariantPrice {
                amount
                currencyCode
              }
              maxVariantPrice {
                amount
                currencyCode
              }
            }
            variants (first:20) {
              edges {
                node {
                  __typename
                  sku
                  id
                  title
                  inventoryQuantity
                  price
                  compareAtPrice
                }
              }
            }
          }
        }
      }
    }
    """
BULK_OPERATION_STATUS = """
{
 currentBulkOperation {
   id
   status
   errorCode
   createdAt
   completedAt
   objectCount
   fileSize
   url
   partialDataUrl
 }
}"""
BULK_OPERATION_STATUS_BY_ID = """query BulkOperationStatusById($id: ID!) {
  node(id: $id) {
    ... on BulkOperation {
      id
      status
      errorCode
      createdAt
      objectCount
      fileSize
      url
      partialDataUrl
    }
  }
}
"""
