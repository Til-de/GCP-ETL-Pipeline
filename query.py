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
        customerLocale
        app
        customer
        email
        note
        tags
        test
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
                marketingEvent {
                    channel
                    id
                    type
                    utmCampaign
                }
                occurredAt
            }
             lastVisit {
                id
                landingPage
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
                occurredAt
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
        taxLines {
          rate
          priceSet {
            shopMoney {
              amount
            }
          }
        }
        subtotalLineItemsQuantity
        cartDiscountAmountSet
        cancelledAt
        cancelReason
        closed
        closedAt
        currencyCode
        presentmentCurrencyCode
        shippingAddress {
            countryCodeV2
            city
            longitude
            latitude
            provinceCode
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
                    createdAt
                    updatedAt
                    lifetimeDuration
                    locale
                    firstName
                    lastName
                    email
                    validEmailAddress
                    phone
                    tags
                    state
                    statistics
                    market {
                        id
                        name
                        handle
                        enabled
                        primary
                    }
                    taxExempt
                    defaultAddress {
                        address1
                        address2
                        city
                        company
                        coordinatesValidated
                        countryCodeV2
                        country
                        latitude
                        longitude
                        province
                        provinceCode
                        timeZone
                        zip
                    }
                    addresses {
                        address1
                        address2
                        city
                        company
                        coordinatesValidated
                        countryCodeV2
                        country
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
                  availableForSale
                  updatedAt
                }
              }
            }
            shippingLine {
                id
                code
                title
                carrierIdentifier
                originalPriceSet
                taxLines
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
