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
        updatedAt
        customerJourneySummary {
            daysToConversion
            customerOrderIndex
            momentsCount
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
                marketingEvent {
                    channel
                    id
                    type
                    utmCampaign
                }
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
                marketingEvent {
                    channel
                    id
                    type
                    utmCampaign
                }
            }
            ready
            moments (first: 20) {
                edges {
                    node {
                        __typename
                        occurredAt

                    }
                }
            }
        }
        app {
          id
        }
        customer {
          id
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
        subtotalLineItemsQuantity
        cancelledAt
        cancelReason
        closed
        closedAt
        presentmentCurrencyCode
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
                    id
                    firstName
                    lastName
                    email
                    phone
                    addresses {
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
                    }
                    emailMarketingConsent {
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
