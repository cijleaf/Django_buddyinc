'use strict';

var appFilter = angular.module('mySunBuddy.filter');

appFilter

//Legend for map
.filter('legend', function($filter) {
    return function(collection, keynames) {

        var keys = [],
            groups = [];
        //Find Key
        angular.forEach(keynames, function(key) {
            var fillterred = $filter('filter')(collection, {
                'role': key
            });
            angular.forEach(fillterred, function(node) {
                groups.push(node);
            });
        });
        return groups;
    };
});