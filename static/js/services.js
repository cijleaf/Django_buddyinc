'use strict';

var appServices = angular.module('mySunBuddy.services');

//api service
appServices.factory("API", function($resource) {
    return $resource('/api', {}, {
        login: {
            method: "POST",
            url: '/api/login'
        },
        register: {
            method: "POST",
            url: '/api/register'
        },
        resetPassword: {
            method: "POST",
            url: '/api/password/reset'
        },
        searchDeals: {
            method: "GET",
            url: '/api/deals',
            isArray: true
        },
        searchInstallationDeals: {
            method: "GET",
            url: '/api/installation/:id/deals',
            isArray: true,
            params: {
                id: '@id'
            }
        },
        previewDeal: {
            method: "POST",
            url: '/api/deals/:id/preview',
            params: {
                id: '@id'
            }
        },
        signDeal: {
            method: "POST",
            url: '/api/deals/:id/sign',
            params: {
                id: '@id'
            }
        },
        denyDeal: {
            method: "POST",
            url: '/api/deals/:id/deny',
            params: {
                id: '@id'
            }
        },
        viewInstallations: {
            method: "GET",
            url: '/api/installations/',
            isArray: true
        },
        retrieveInstallation: {
            method: "GET",
            url: '/api/installation/:id',
            params: {
                id: '@id'
            }
        },
        updateSolarPercent: {
            method: "POST",
            url: '/api/solar/percent'
        },
        editAccount: {
            method: "POST",
            url: '/api/account/edit'
        },
        setupSellerFunding: {
            method: "POST",
            url: '/api/account/seller_setup'
        },

        setupBeneficialOwner: {
            method: "POST",
            url: '/api/account/beneficial_setup'
        },
        getBeneficialOwners: {
            method: "GET",
            url: '/api/account/get_all_beneficials',
            isArray: true
        },
        certifyOwnership: {
            method: "GET",
            url: '/api/account/certify_ownership'
        },

        buyerAutomatch: {
            method: "POST",
            url: '/api/buyer/automatch'
        },
        saveCommunityCode: {
            method: "POST",
            url: '/api/buyer/code'
        },
        createInstallation: {
            method: "POST",
            url: '/api/create_installation'
        },
        editInstallation: {
            method: "PUT",
            url: '/api/installation/:id/edit',
            params: {
                id: '@id'
            }
        },
        calculateCredits: {
            method: "POST",
            url: '/api/credit/calculate/:id',
            params: {
                id: '@id'
            }
        },
        getInstallationTransactions: {
            method: "GET",
            url: '/api/installation/:id/transactions',
            params: {
                id: '@id'
            }
        },
        emailInstallationCustomers: {
            method: "POST",
            url: '/api/installation/:id/send_email',
            params: {
                id: '@id'
            }
        },
        retrieveReportData: {
            method: "GET",
            url: '/api/reportData'
        },
        getIavToken: {
            method: "GET",
            url: '/api/get-iav-token'
        },
        updateFunding: {
            method: "POST",
            url: '/api/update-funding'
        },
        removeFunding: {
            method: "POST",
            url: '/api/remove-funding'
        },
        verifyDeposits: {
            method: "POST",
            url: '/api/account/verify-deposits'
        },
        getBusinessClassifications: {
            method: "GET",
            url: '/api/business-classification',
            isArray: true
        },
        getProfile: {
            method: "GET",
            url: '/api/get-profile'
        },
    });
});

appServices.factory("Alert", function() {
    function setOptions() {
        toastr.options = {
            positionClass: 'toast-top-center'
        };
    }
    return {
        showError: function(msg, clear) {
            setOptions();
            if (clear) {
                toastr.clear();
            }
            toastr.error(msg);
        },
        showSuccess: function(msg, clear) {
            setOptions();
            if (clear) {
                toastr.clear();
            }
            toastr.success(msg);
        },
        showInfo: function(msg, clear) {
            setOptions();
            if (clear) {
                toastr.clear();
            }
            toastr.info(msg);
        },
        showProgress: function(msg, clear) {
            setOptions();
            toastr.options.progressBar = true;
            toastr.options.closeDuration = 1000 * 1000;
            if (clear) {
                toastr.clear();
            }
            toastr.info(msg);
        }
    };
});


appServices.factory("utils", function(Alert) {
    function parseError(error) {
        var errors = [];
        if (angular.isString(error.data)) {
            errors.push(error.data);
        } else {
            angular.forEach(error.data, function(message, key) {
                if (angular.isArray(message)) {
                    errors = errors.concat(message);
                } else {
                    errors.push(message);
                }
            });
        }
        return errors;
    }
    return {
        parseError: parseError,
        handleError: function(error) {
            var errors = parseError(error);
            Alert.showError(errors.join(","));
        }
    };
});


appServices.factory("installationService", function() {
    return {
        format: function(data) {
            var installation_obj = {
                "id": data.id,
                "name": data.name,
                "address": data.address,
                "city": data.city,
                "state": data.state,
                "zip_code": data.zip_code,
                "is_active": data.is_active,
                "average_monthly_credit": data.average_monthly_credit,
                "credit_to_sell_percent": data.credit_to_sell_percent,
                "credit_to_sell": data.credit_to_sell,
                "remaining_credit": data.remaining_credit,
                "load_zone": data.load_zone,
                "community_code": data.community_code,
                "utility_provider": data.utility_provider,
                "utility_api_uid": data.utility_api_uid,
                "utility_meter_uid": data.utility_meter_uid,
                "utility_service_identifier": data.utility_service_identifier,
                "utility_last_updated": data.utility_last_updated,
                "active_deals": data.active_deals,
                "pending_deals": data.pending_deals,
                "left": data.left,
                "earnings": data.earnings,
                "transactions": data.transactions
            };
            return installation_obj;
        }
    }
});


appServices.factory("behaviorExperiment", function($location) {
    const labels = ['CF', 'CFR', 'IF', 'IFR'];

    function variationToLabel(variation) {
        if (variation >= 0 && variation < labels.length)
            return labels[variation];
        else
            return "";
    }

    function getChosenVariationLabel() {
        let currentVariation = cxApi.getChosenVariation();
        return variationToLabel(currentVariation);
    }

    function pathToVariation() {
        return labels.indexOf($location.path().slice(1));
    }

    function isExperimentEnabled() {
        return config.googleAnalyticsExperimentKey && $location.host().startsWith("campaign.");
    }

    function chooseLandingPage (defaultLandingPage) {
        // Let the user choose a variation (through the URL)
        // only if GA hasn't chosen one already.
        if (cxApi.getChosenVariation() === cxApi.NO_CHOSEN_VARIATION) {
            let fixedVariation = pathToVariation();
            if (fixedVariation !== -1) {
                cxApi.setChosenVariation(fixedVariation);
            }
        }
        // chose a variation or get the one previously chosen
        let currentVariation = cxApi.chooseVariation();
        // get the landing page path or use the default one if can't find one
        return variationToLabel(currentVariation) || defaultLandingPage;
    }

    return {
        getVariationLabel: variationToLabel,
        getChosenVariationLabel: getChosenVariationLabel,
        pathToVariation: pathToVariation,
        isExperimentEnabled: isExperimentEnabled,
        chooseLandingPage: chooseLandingPage,
    }
});


appServices.factory("gapi", function() {
    return {
        sendSocial: function(network, action, target) {
            if (ga) {
                ga('send', 'social', network, action, target);
            }
        }
    }
});
