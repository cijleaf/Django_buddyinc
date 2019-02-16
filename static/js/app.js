'use strict';

var app = angular.module('mySunBuddy', ['ngRoute','ngResource','ngSanitize','ngDropdowns','ngPasswordStrength',
                                        'flow','angular-progress-arc','angular.vertilize','angularAwesomeSlider',
                                        'angular-loading-bar', 'pdf','perfect_scrollbar','ngFileUpload', 'ngCookies',
                                        'duScroll', 'ngMap', 'mySunBuddy.common', 'mySunBuddy.dashboard',
                                        'mySunBuddy.public', 'mySunBuddy.services', 'mySunBuddy.filter',
                                        'mySunBuddy.controllers', 'angulartics', 'angulartics.google.analytics',
                                        'usPhone', 'selectState', '720kb.datepicker']);

app.constant("config", window.config);

app.constant('ConfigURLs', config);

//used in edit account controller and the two sign up controllers
app.factory("currentUser", function() {
    var user = {
        /**
         * Set user data
         * @param data the user data
         */
        update: function(data) {
            user.authenticated = data && data.id;
            if (data.role == 'buyer') {
                data.thumbnail = '/static/i/pic-buyer.jpg'
            } else if (data.role == 'seller') {
                data.thumbnail = '/static/i/pic-seller.jpg'
            } else if (data.role == 'community_solar') {
                data.thumbnail = '/static/i/pic-seller.jpg'
            }
            user.profile = data;
        }
    };
    user.update(window.user || {});
    return user;
});

// Initialize the main module
app.run(function($rootScope, $uibModalStack, $location, $window, $route, currentUser) {

    $uibModalStack.dismissAll();

    $rootScope.currentUser = currentUser;
    $rootScope.location = $location;

    $rootScope.$on('$locationChangeStart', function(ev, next, current) {
        var nextPath = $location.path(),
            nextRoute = $route.routes[nextPath];
        if (nextPath == "/Landing" && currentUser.authenticated && currentUser.profile) {
            if (currentUser.profile.role == "buyer") {
                $location.path("/Buyer_Account_Portal");
            } else if (currentUser.profile.role == "seller") {
                $location.path("/Seller");
            } else if (currentUser.profile.role == "community_solar") {
                $location.path("/Community_Account_Portal");
            }
        }
        if (nextRoute && nextRoute.auth && (!currentUser.authenticated || !currentUser.profile || currentUser.profile.role != nextRoute.role)) {
            $location.path("/Landing");
        }
    });

    // make sure Google Analytics is updated
    $rootScope.$on('$routeChangeSuccess', function(event) {
      $window.ga('send', 'pageview', { page: $location.url() });
    });
});

//make django and angular work well
app.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});

let chooseLandingPage = {_: function ($location, behaviorExperiment) {
    let landing = "Landing";
    if (behaviorExperiment.isExperimentEnabled()) {
        landing = behaviorExperiment.chooseLandingPage(landing);
    }
    $location.path("/" + landing);
}};

app.config(["$routeProvider", "$locationProvider",
    function($routeProvider) {
        $routeProvider
            .when("/Landing", {
                templateUrl: "static/partials/Landing.html",
                controller: 'homeController',
                resolve: chooseLandingPage,
            })
            .when("/CF", {
                templateUrl: "static/partials/LandingCF.html",
                controller: 'homeController',
                resolve: chooseLandingPage,
            })
            .when("/CFR", {
                templateUrl: "static/partials/LandingCFR.html",
                controller: 'homeController',
                resolve: chooseLandingPage,
            })
            .when("/IF", {
                templateUrl: "static/partials/LandingIF.html",
                controller: 'homeController',
                resolve: chooseLandingPage,
            })
            .when("/IFR", {
                templateUrl: "static/partials/LandingIFR.html",
                controller: 'homeController',
                resolve: chooseLandingPage,
            })
            .when("/Seller", {
                templateUrl: "static/partials/Seller.html",
                controller: 'sellerController',
                auth: true,
                role: "seller"
            })
            .when("/Sign_Up_Seller", {
                templateUrl: "static/partials/Sign_Up.html",
                controller: 'signUpController',
                role: "seller"
            })
            .when("/Sign_Up_Buyer", {
                templateUrl: "static/partials/Sign_Up.html",
                controller: 'signUpController',
                role: "buyer"
            })
            .when("/Seller_Account_Portal", {
                templateUrl: "static/partials/Account_Portal.html",
                controller: 'portalController',
                css: 'static/css/account-portal.css',
                auth: true,
                role: "seller"
            })
            .when("/Buyer_Account_Portal", {
                templateUrl: "static/partials/Account_Portal.html",
                controller: 'portalController',
                css: 'static/css/account-portal.css',
                auth: true,
                role: "buyer"
            })
            .when("/Community_Account_Portal", {
                templateUrl: "static/partials/Community_Account_Portal.html",
                controller: 'communityPortalController',
                css: 'static/css/account-portal.css',
                auth: true,
                role: "community_solar"
            })
            .when("/Installation_Portal/:id", {
                templateUrl: "static/partials/Installation_Portal.html",
                controller: 'installationPortalController',
                css: 'static/css/account-portal.css',
                auth: true,
                role: "community_solar"
            })
            .when("/Installation_Transactions/:id", {
                templateUrl: "static/partials/Installation_Transactions.html",
                controller: 'installationTransactionsController',
                css: 'static/css/account-portal.css',
                auth: true,
                role: "community_solar"
            })
            .when('/FAQ', {
                auth: false,
                controller: 'FAQController',
                templateUrl: 'static/partials/FAQ.html'
            })
            .otherwise({
                redirectTo: '/Landing'
            });
    }
]);
