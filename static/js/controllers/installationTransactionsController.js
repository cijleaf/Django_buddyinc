var appControllers = angular.module('mySunBuddy.controllers');
//Finish Sign-Up Portal
appControllers.controller('installationTransactionsController', function($scope, $rootScope, $timeout, $location, API, Upload,
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

    $scope.profile = {};
    angular.extend($scope.profile, currentUser.profile);

    $scope.transactions = {};
    $scope.offset = 0; //multiples of limit, which is currently 25
    $scope.limit = 25
    //Get Match
    $scope.getTransactions = function (offset, limit) {
        API.getInstallationTransactions({
            id: $routeParams.id,
            limit: limit,
            offset: offset
        }).$promise.then(function(transactions) {
            var transaction_list = [];
            angular.forEach(transactions.results, function(data) {
                var transaction = {
                    "id": data.id,
                    "info": {
                        "date": data.bill_statement_date,
                        "buyer": data.deal.buyer.name,
                        "amount": data.paid_to_seller,
                        "status": data.status
                    }
                };
                transaction_list.push(transaction);
            });
            $scope.transactions = transaction_list;
        }).catch(utils.handleError);
    };
    $scope.getTransactions($scope.offset, $scope.limit);

    $scope.viewNextTransactions = function() {
        $scope.offset = $scope.offset + $scope.limit
        $scope.getTransactions($scope.offset, $scope.limit);
    };

    $scope.viewPreviousTransactions = function() {
        $scope.offset = $scope.offset - $scope.limit
        $scope.getTransactions($scope.offset, $scope.limit);
    };

});
