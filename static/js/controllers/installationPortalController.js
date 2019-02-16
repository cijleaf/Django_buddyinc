var appControllers = angular.module('mySunBuddy.controllers');
//Finish Sign-Up Portal
appControllers.controller('installationPortalController', function($scope, $rootScope, $timeout, $location, API, Upload,
    $uibModal, Alert, utils, $cookies, $filter, $window, ConfigURLs, currentUser, $route, $routeParams, installationService) {

    $scope.role = $route.current.$$route.role;

    $scope.installation = $rootScope.installation;

    $scope.retrieveInstallation = function() {
        API.retrieveInstallation({
            id: $routeParams.id
        }).$promise.then(function(data) {
            $scope.installation = installationService.format(data);
        }).catch(utils.handleError);
    };
    $scope.retrieveInstallation();

    $scope.saveButton = true;

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

    $scope.module = {
        summary: {
            percentage: Math.round($scope.profile.credit_to_sell_percent) / 100,
            quarter: [],
            solar: {},
            info: {},
            list: {},
            map: {
                shape: [],
                track: [],
                selectPoint: {
                    id: 0
                },
                info: {}
            },
            status: {
                dwolla: {
                    account: '',
                    fundingSource: ''
                }
            }
        },
        notifications: {
            store: {
                percentage: 0
            },
            list: []
        },
        historical: {
            list: []
        }
    };
    //Get Summary
    $scope.module.summary.solar = {
        value: 1,
        options: {
            from: 1,
            to: 100,
            step: 1,
            dimension: '%',
            vertical: false,
            limits: false,
            scale: ['1%', '|', '25%', '|', '50%', '|', '75%', '|', '100%']
        }
    };

    $scope.matches = {};
    //Get Match
    $scope.searchDeals = function () {
        API.searchInstallationDeals({
            id: $routeParams.id
        }).$promise.then(function(matches) {
            $scope.module.summary.info.title = "You have " + matches.length + " open match(es).";
            var match_list = [];
            var direction = 0.1;
            angular.forEach(matches, function(data) {
                var left = (new Date(data.end_date).getTime() - new Date().getTime()) / (3600 * 24 * 1000);
                var match_obj = {
                    "id": data.id,
                    "connect": true,
                    "info": {
                        "id": data.id,
                        "status": data.status,
                        "start": data.start_date,
                        "end": data.end_date,
                        "thumb": "static/i/pic-buyer.jpg",
                        "name": data.buyer.email,
                        "amounts": $filter("currency")(data.price),
                        "power": data.quantity / 1000,
                        "time_remain": left > 0 ? parseInt(left, 10) : 0,
                    }
                };
                match_list.push(match_obj);
            });
            $scope.matches = match_list;
        }).catch(utils.handleError);
    };
    $scope.searchDeals();

    // Boolean variable to handle display of Active deals and Pending deals
    $scope.active = 'active';

    //UtilityAPI
    $scope.utilityapiurl = ConfigURLs['utilityAPIPortalUrl'];

    $scope.googleMapsUrl = "//maps.google.com/maps/api/js?key=" + ConfigURLs.googleMapsApiKey;

    $scope.validAddresses = [];

    $scope.checking = false;

    //apply solar percentage
    $scope.applySolarProduction = function() {
        $scope.solar.value = parseInt($scope.module.summary.solar.value, 10);
    };

    $scope.editInstallationInfo = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Edit_Installation.html',
            controller: 'editInstallationController',
            resolve: {
                installation: function () {
                    return $scope.installation;
                }
            }
        });
        modalInstance.result.then(function (installation) {
            $scope.installationChanges = installation;
            angular.extend($scope.installation, $scope.installationChanges);
        }, function () {});
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

    $scope.calculateCredits = function() {
        $scope.installation.module_types = $scope.profile.module_types;
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Calculate_Credits.html',
            controller: 'calculateCreditsController',
            resolve: {
                installation: function () {
                    return $scope.installation;
                }
            }
        });
        modalInstance.result.then(function (installation) {
            $scope.retrieveInstallation();
        }, function () {});
    }

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

    $scope.signDeal = function(match) {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Sign_Deal.html',
            controller: 'signDealModalController',
            resolve: { match: match }
        });

        modalInstance.result.then(function () {
                $scope.searchDeals();
                $scope.retrieveInstallation();
        }, function () {
        });
    };

    $scope.reject = function(match) {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Reject_Sale.html',
            controller: 'rejectSaleModalController',
            resolve: {
                match: match
            }
        });
        modalInstance.result.then(function () {
                $scope.searchDeals();
        }, function () {
        });
    };

    $scope.emailCustomers = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Email_Customers.html',
            controller: 'emailCustomersController',
            resolve: {
                installation: function () {
                    return $scope.installation;
                }
            }
        });
        modalInstance.result.then(function (installation) {
            $scope.installationChanges = installation;
            angular.extend($scope.installation, $scope.installationChanges);
        }, function () {});
    };

});
