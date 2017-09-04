/*
 * Runek
 * http://www.scoopthemes.com/
 *
 * Copyright (c) 2014, ScoopThemes
 * Licensed under the BSD license.
 */
'use strict';

var appMaster = {

    preLoader: function(){
        var imageSources = [];
        $('img').each(function() {
            var sources = $(this).attr('src');
            imageSources.push(sources);
        });
        if($(imageSources).load()){
            $('.pre-loader').fadeOut('slow');
        }
    },

    navSpy: function(){
        /* affix the navbar after scroll below header */
        $('#nav.navbar-static-top').affix({
            offset: {
                top: $(window).height()
            }
        });

        /* highlight the top nav as scrolling occurs */
        $('body').scrollspy({
            target: '#nav'
        });
    },

    smoothScroll: function() {
        // Smooth Scrolling
        $('a[href*=#]:not([href=#carousel-example-generic], [href=#testimonials-carousel])').click(function() {
            if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {

                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                if (target.length) {
                    $('html,body').animate({
                        scrollTop: target.offset().top
                    }, 1000);
                    return false;
                }
            }
        });
    },

    scrollToTop: function(){
        /* smooth scrolling for scroll to top */
        $('.scroll-top').click(function() {
            $('body,html').animate({
                scrollTop: 0
            }, 1000);
        });
    },

    revSlider: function(){

        var docHeight = $(window).height();
        
        var revapi;
        revapi = jQuery('.tp-banner').revolution(
        {
            delay: 4000,
            startwidth: 1170,
            startheight: docHeight,
            hideThumbs: 10,
            fullWidth: "off",
            fullScreen: "on",
            onHoverStop: "off",
            autoHeight:"on",
            hideTimerBar:"on",
            touchenabled:"off",
            fullScreenOffsetContainer: "",
            navigationArrows:"none",
            dottedOverlay: 'none',
            navigationType:"none",
        });
    },

    stellar: function(){
        $(window).stellar();
    },

    skillsChart: function(){
        $('.chart').easyPieChart({
            animate: 2000,
            size: 180,
            lineWidth:10,
            barColor: "#22a3df"
        });
    },


    isoTop: function(){
        var $container = $('#container');
        // init
        $container.isotope({
            // options
            itemSelector: '.item'
        });

        $('#filters').on('click', 'button', function() {
            $('#filters button').removeClass("current");
            $(this).addClass("current");
            var filterValue = $(this).attr('data-filter');
            $container.isotope({
                filter: filterValue
            });
        });
    },

    animateScript: function() {
        $('.scrollpoint.sp-effect1').waypoint(function(){$(this).toggleClass('active');$(this).toggleClass('animated fadeInLeft');},{offset:'100%'});
       $('.scrollpoint.sp-effect2').waypoint(function(){$(this).toggleClass('active');$(this).toggleClass('animated fadeInRight');},{offset:'100%'});
       $('.scrollpoint.sp-effect3').waypoint(function(){$(this).toggleClass('active');$(this).toggleClass('animated fadeInDown');},{offset:'100%'});
       $('.scrollpoint.sp-effect4').waypoint(function(){$(this).toggleClass('active');$(this).toggleClass('animated fadeIn');},{offset:'100%'});
       $('.scrollpoint.sp-effect5').waypoint(function(){$(this).toggleClass('active');$(this).toggleClass('animated fadeInUp');},{offset:'100%'});
       $('.scrollpoint.sp-effect6').waypoint(function(){$(this).toggleClass('active');$(this).toggleClass('animated bounceIn');},{offset:'100%'});
    },

    canvasHack: function(){
        // so non-IE won't freak out in canvasInit
        var G_vmlCanvasManager; 

        function canvasInit() {
            var cv = document.createElement('canvas');
            if (G_vmlCanvasManager != undefined) { // ie IE
                G_vmlCanvasManager.initElement(cv);
            }

            if (cv.getContext) {
                var ctx = cv.getContext('2d');
            }
        }
    }



};


$(document).ready(function() {

    appMaster.scrollToTop();

});