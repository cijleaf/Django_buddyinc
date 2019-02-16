var appControllers = angular.module('mySunBuddy.controllers');
//Finish Sign-Up Portal
appControllers.controller('portalController', function($scope, $rootScope, $timeout, $location, API, Upload,
    $uibModal, Alert, utils, $cookies, $window, ConfigURLs, currentUser, $route, gapi, $analytics) {

    $scope.role = $route.current.$$route.role;

    $scope.saveButton = true;
    $scope.showIavSetupButton = true;
    $scope.showDocumentUploadButton = true;
    $scope.documentUploaded = false;

    $scope.profile = {};
    angular.extend($scope.profile, currentUser.profile);

    var creditPercent;

    if ($scope.role=='seller') {
        creditPercent = $scope.profile.credit_to_sell_percent;
    }

    $scope.solar = {
        value: creditPercent || 0,
        options: {
            from: 0,
            to: 100,
            step: 1,
            dimension: '%',
            vertical: false,
            limits: false,
            scale: ['0%', '25%', '50%', '75%', '100%']
        }
    };

    $scope.showSolarPercentSlider = false;

    //UtilityAPI
    $scope.utilityapiurl = ConfigURLs['utilityAPIPortalUrl'];

    $scope.dwollaRegisterUrl = ConfigURLs['dwollaOauthUrl'];

    $scope.dwollaLoginUrl = ConfigURLs['dwollaLoginOauthUrl'];

    $scope.googleMapsUrl = "//maps.google.com/maps/api/js?key=" + ConfigURLs.googleMapsApiKey;

    $scope.validAddresses = [];

    $scope.checking = false;

    //apply solar percentage
    $scope.applySolarProduction = function() {
        $scope.solar.value = parseInt($scope.module.summary.solar.value, 10);
    };

    $scope.editPersonalInfo = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Edit_Account.html',
            controller: 'editAccountController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function (profile) {
            $scope.profileChanges = profile;
            angular.extend($scope.profile, $scope.profileChanges);
        }, function () {});
    };

    $scope.toMarketplace = function() {
        if(!$scope.profile.complete) {
            return;
        } else {
            $location.path("/Seller");
        }
    };

    $scope.savePercentage = function() {
        if (!$scope.saveButton) {
            return;
        };
        $scope.saveButton = false;
        API.updateSolarPercent({
            percent: $scope.solar.value
        }).$promise.then(function(profile){
            currentUser.update(profile);
            angular.extend($scope.profile, currentUser.profile);
            $scope.saveButton = true;
        }).catch(utils.handleError).finally(function() {
            $scope.saveButton = true;
        });
    };

    $scope.enterMarket = function() {
        API.buyerAutomatch().$promise.then(function(profile){
            currentUser.update(profile);
            angular.extend($scope.profile, currentUser.profile);
        }).catch(utils.handleError);
    };

    $scope.matchCommunitySolar = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Community_Code.html',
            controller: 'communityCodeController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function (profile) {
            $scope.profileChanges = profile;
            angular.extend($scope.profile, $scope.profileChanges);
        }, function () {});
    };

	// jsSocials
    $scope.incompleteProfile = true;
    $scope.bindJsSocials = function () {
        API.retrieveReportData().$promise
            .then(function(response) {
                if (!response.reportData || !response.landingPage) {
                    return;
                }

                $scope.incompleteProfile = response.incompleteProfile;

                let url = window.location.origin + window.location.pathname;
                $(".share").jsSocials({
                    url: url,
                    text: response.reportData,
                    showCount: false,
                    shareIn: "popup",
                    shares: [{share: "facebook", label: "Share"}, "twitter", "linkedin"],
                    on: {
                        click: function(event) {
                            $analytics.eventTrack(this.share, {
                                category: 'social',
                                label: response.landingPage
                            });
                            gapi.sendSocial(this.share, this.label.toLowerCase(), this.url);
                            // make sure Google Analytics is updated with the share click
                            $rootScope.sendGA = function(event) {
                                var eventActionText = 'User clicked: ' + this.label.toLowerCase();
                                $window.ga('send', {
                                    hitType: 'event',
                                    eventCategory: 'Social',
                                    eventAction: eventActionText
                                });
                            }
                        }
                    }
                });
            });
    };

    $scope.shouldDisableShareButtons = function() {
        if ($scope.incompleteProfile)
            return "disabled-buttons";
    };

    $scope.shouldShowIncompleteProfileTooltip = function () {
        if ($scope.incompleteProfile)
            return "Please complete your profile to be able to share!";
    };

    $scope.isFundableStatus = function () {
        if ($scope.profile.current_status == 'document') {
            return false;
        }

        if ($scope.profile.current_status == 'suspended') {
            return false;
        }

        return true;
    };

    $scope.removeFunding = function () {
        if (confirm("Do you really want to remove this funding source?")){

            API.removeFunding().$promise.then(function(response) {
                Alert.showSuccess('Funding source removed successfully!');

                $scope.profile.funding_id = null;
                $scope.profile.funding_source_name = null;
                $scope.profile.funding_status = null;
                $scope.profile.complete = false;

                currentUser.profile.funding_id = null;
                currentUser.profile.funding_source_name = null;
                currentUser.profile.funding_status = null;
                $scope.profile.complete = false;

                $scope.showIavSetupButton = true;

            }).catch(function () {
                Alert.showError('An error has occurred, please contact support.');
            });
        }
    };

    $scope.setupBeneficialOwner = function () {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Beneficial_Owner.html',
            controller: 'setupBeneficialOwnerController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function (r) {
            Alert.showSuccess('A beneficial owner added successfully!');
            $scope.profile.beneficial_count++;
            currentUser.profile.beneficial_count++;
        });
    };

    $scope.viewBeneficialDetails = function () {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Beneficial_Table.html',
            controller: 'certifyOwnershipController'

        });
    };

    $scope.setupIavForSeller = function() {

        if ($scope.profile.current_status == 'verified') {
            $scope.setupIav();

            return;
        }

        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Setup_Seller_Funding.html',
            controller: 'setupSellerFundingController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });

        modalInstance.result.then(function () {
            $scope.showIavSetupButton = false;

            API.getProfile().$promise.then(function(response) {
                $scope.profile = response;
                currentUser.profile = response;
                $scope.showIavSetupButton = true;

                if ($scope.profile.current_status == 'verified') {
                    $scope.setupIav();
                }

                if ($scope.profile.current_status == 'unverified') {
                    $scope.setupIav();
                }
            });
        });
    };

    $scope.setupIav = function () {
        API.getIavToken().$promise.then(function (response) {
            ConfigURLs['currentIavToken'] = response.token;
            $scope.showIavSetupButton = false;
            dwolla.configure(ConfigURLs['useFake'] ? 'sandbox' : 'prod');
            dwolla.iav.start(ConfigURLs['currentIavToken'], {
                container: 'iavContainer',
                microDeposits: true,
                fallbackToMicroDeposits: true
            }, function(err, res) {
                if (err) {
                    console.log(err);
                    Alert.showError('An error has occurred, please contact support.');
                }

                API.updateFunding().$promise.then(function(response) {
                    if(response.fundingStatus == 'verified'){
                        Alert.showSuccess('Funding source added successfully!');
                    }

                    $scope.profile.funding_id = response.fundingId;
                    $scope.profile.funding_source_name = response.fundingSource;
                    $scope.profile.funding_status = response.fundingStatus;
                    $scope.profile.complete = response.has_complete_profile;

                    currentUser.profile.funding_id = response.fundingId;
                    currentUser.profile.funding_source_name = response.fundingSource;
                    currentUser.profile.funding_status = response.fundingStatus;
                    currentUser.profile.complete = response.has_complete_profile;

                }).catch(function () {
                    Alert.showError('An error has occurred, please contact support.');
                });
            });
        }).catch(function () {
            Alert.showInfo('Your account is being verified. Please try again later.');
        });
    };

    $scope.uploadDocument = function () {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Upload_Verification_Document.html',
            controller: 'uploadVerificationDocumentController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });

        modalInstance.result.then(function () {
            $scope.documentUploaded = true;
        });
    };

    $scope.verifyDeposits = function () {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Verify_Deposits.html',
            controller: 'verifyDepositsController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });

        modalInstance.result.then(function (response) {
            $scope.profile.funding_status = response.funding_status;

            if(response.funding_status == "verified"){
                Alert.showSuccess('Funding source verified successfully!');
            }else{
                Alert.showError('Verification Failed.');
            }
        });
    };
});
