/**
 * Auto-generated Decision Tree Phishing Predictor.
 * Trained on UCI PhiUSIIL dataset.
 * Returns the probability of the URL being phishing (0.0 to 1.0).
 */
function predictPhishing(features) {
    if (features['qty_slash'] <= 2.5000) {
      if (features['is_https'] <= 0.5000) {
        return 1.0000;
      } else {
        if (features['url_length'] <= 46.5000) {
          if (features['qty_dot'] <= 1.5000) {
            return 1.0000;
          } else {
            if (features['qty_digits'] <= 4.5000) {
              if (features['qty_subdomains'] <= 1.5000) {
                if (features['qty_hyphen'] <= 1.5000) {
                  if (features['digit_ratio'] <= 0.1404) {
                    if (features['qty_subdomains'] <= 0.5000) {
                      if (features['digit_ratio'] <= 0.1297) {
                        return 0.0035;
                      } else {
                        return 0.0784;
                      }
                    } else {
                      if (features['qty_dot'] <= 2.5000) {
                        return 1.0000;
                      } else {
                        return 0.0049;
                      }
                    }
                  } else {
                    if (features['qty_subdomains'] <= 0.5000) {
                      if (features['domain_length'] <= 15.5000) {
                        return 0.2340;
                      } else {
                        return 0.0455;
                      }
                    } else {
                      if (features['qty_dot'] <= 2.5000) {
                        return 1.0000;
                      } else {
                        return 0.2500;
                      }
                    }
                  }
                } else {
                  if (features['qty_subdomains'] <= 0.5000) {
                    if (features['qty_digits'] <= 3.5000) {
                      if (features['qty_digits'] <= 0.5000) {
                        return 0.0039;
                      } else {
                        return 0.1111;
                      }
                    } else {
                      if (features['domain_length'] <= 25.0000) {
                        return 0.0000;
                      } else {
                        return 1.0000;
                      }
                    }
                  } else {
                    if (features['qty_dot'] <= 2.5000) {
                      return 1.0000;
                    } else {
                      if (features['domain_length'] <= 30.5000) {
                        return 0.0000;
                      } else {
                        return 0.5714;
                      }
                    }
                  }
                }
              } else {
                if (features['qty_dot'] <= 3.5000) {
                  return 1.0000;
                } else {
                  if (features['qty_hyphen'] <= 0.5000) {
                    if (features['qty_subdomains'] <= 3.5000) {
                      if (features['qty_subdomains'] <= 2.5000) {
                        return 0.0132;
                      } else {
                        return 0.2381;
                      }
                    } else {
                      return 1.0000;
                    }
                  } else {
                    if (features['domain_length'] <= 28.0000) {
                      return 0.0000;
                    } else {
                      if (features['qty_letters'] <= 31.5000) {
                        return 0.9600;
                      } else {
                        return 0.4286;
                      }
                    }
                  }
                }
              }
            } else {
              if (features['url_length'] <= 21.5000) {
                return 0.3333;
              } else {
                if (features['qty_hyphen'] <= 2.5000) {
                  if (features['url_length'] <= 34.5000) {
                    if (features['digit_ratio'] <= 0.1970) {
                      if (features['qty_subdomains'] <= 1.5000) {
                        return 0.0000;
                      } else {
                        return 1.0000;
                      }
                    } else {
                      if (features['qty_hyphen'] <= 0.5000) {
                        return 1.0000;
                      } else {
                        return 0.6667;
                      }
                    }
                  } else {
                    return 1.0000;
                  }
                } else {
                  return 0.0000;
                }
              }
            }
          }
        } else {
          if (features['qty_subdomains'] <= 0.5000) {
            if (features['qty_letters'] <= 43.5000) {
              return 0.0000;
            } else {
              if (features['domain_length'] <= 41.5000) {
                return 0.2500;
              } else {
                return 0.0000;
              }
            }
          } else {
            if (features['digit_ratio'] <= 0.0079) {
              if (features['qty_dot'] <= 3.5000) {
                if (features['qty_subdomains'] <= 1.5000) {
                  if (features['qty_dot'] <= 2.5000) {
                    return 1.0000;
                  } else {
                    return 0.0000;
                  }
                } else {
                  return 1.0000;
                }
              } else {
                if (features['url_length'] <= 51.5000) {
                  return 0.0000;
                } else {
                  return 1.0000;
                }
              }
            } else {
              return 1.0000;
            }
          }
        }
      }
    } else {
      return 1.0000;
    }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { predictPhishing };
}
