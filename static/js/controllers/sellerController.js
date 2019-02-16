var appControllers =angular.module('mySunBuddy.dashboard.seller');
//Seller
appControllers.controller('sellerController', function($scope, $rootScope, $timeout,
    $window, $uibModal, $filter, $location, currentUser, API, Alert, utils) {

    if (!currentUser.profile.complete) {
        $location.path("/Seller_Account_Portal");
    }

    //limit
    $scope.limit = {
        shape: 2,
        historical: 5
    };

    $rootScope.role = 'Seller';
    $scope.profile = {};
    angular.extend($scope.profile, currentUser.profile);

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
    $scope.role = 'seller';

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

    $scope.denying = false;
    $scope.denyDeal = function(notification) {
        if ($scope.denying) {
            return;
        }
        $scope.denying = false;
        API.denyDeal({
            id: notification.deal.id
        }).$promise.then(function() {
            notification.deny = true;
            //reload notification widget.
            loadNotifications()
        }).catch(utils.handleError).finally(function() {
            $scope.denying = false;
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
        }, function () {
        });
    };

    //Tabs
    $scope.module.summary.show = true;

    $scope.matches = {};

    //Get Match
    $scope.searchDeals = function () {
        API.searchDeals().$promise.then(function(matches) {
            $scope.module.summary.info.title = "We found " + matches.length + " matches in your area.";
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

    //Add Market
    $scope.showSelectPoint = function(event, obj) {
        // not implemented
    };
    //Show Map
    $scope.showMap = function(historical) {
        // not implemented
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

});
