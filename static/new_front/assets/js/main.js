!(function (e) {
    "use strict";
    jQuery(document).on("ready", function () {
        function t() {
            e(".newsletter-form").addClass("animated shake"),
                setTimeout(function () {
                    e(".newsletter-form").removeClass("animated shake");
                }, 1e3);
        }
        function a(t, a) {
            if (t) var s = "validation-success";
            else s = "validation-danger";
            e("#validator-newsletter").removeClass().addClass(s).text(a);
        }
        e(window).on("scroll", function () {
            e(this).scrollTop() > 120 ? e(".navbar-area").addClass("is-sticky") : e(".navbar-area").removeClass("is-sticky");
        }),
            jQuery(".mean-menu").meanmenu({ meanScreenWidth: "991" }),
            e(".home-slides").owlCarousel({
                loop: !0,
                nav: !0,
                dots: !1,
                autoplayHoverPause: !0,
                autoplay: !0,
                smartSpeed: 1e3,
                animateOut: "slideOutLeft",
                animateIn: "slideInRight",
                items: 1,
                navText: ["<i class='flaticon-left-chevron'></i>", "<i class='flaticon-right-chevron'></i>"],
            }),
            // e(".home-slides").on("translate.owl.carousel", function () {
            //     e(".main-banner-content .sub-title").removeClass("animated fadeInLeft").css("opacity", "0"),
            //         e(".main-banner-content h1").removeClass("animated fadeInLeft").css("opacity", "0"),
            //         e(".main-banner-content .btn-box").removeClass("animated fadeInLeft").css("opacity", "0");
            // }),
            // e(".home-slides").on("translated.owl.carousel", function () {
            //     e(".main-banner-content .sub-title").addClass("animated fadeInLeft").css("opacity", "1"),
            //         e(".main-banner-content h1").addClass("animated fadeInLeft").css("opacity", "1"),
            //         e(".main-banner-content .btn-box").addClass("animated fadeInLeft").css("opacity", "1");
            // }),
            e(function () {
                e(".default-btn")
                    .on("mouseenter", function (t) {
                        var a = e(this).offset(),
                            s = t.pageX - a.left,
                            i = t.pageY - a.top;
                        e(this).find("span").css({ top: i, left: s });
                    })
                    .on("mouseout", function (t) {
                        var a = e(this).offset(),
                            s = t.pageX - a.left,
                            i = t.pageY - a.top;
                        e(this).find("span").css({ top: i, left: s });
                    });
            }),
            e(".services-slides").owlCarousel({
                loop: !0,
                nav: !0,
                dots: !0,
                autoplayHoverPause: !0,
                autoplay: !0,
                margin: 30,
                navText: ["<i class='flaticon-left-chevron'></i>", "<i class='flaticon-right-chevron'></i>"],
                responsive: { 0: { items: 1 }, 576: { items: 2 }, 768: { items: 2 }, 1200: { items: 3 } },
            }),
            e(".main-services-slides").owlCarousel({
                loop: !0,
                nav: !1,
                dots: !0,
                autoplayHoverPause: !0,
                autoplay: !0,
                margin: 30,
                navText: ["<i class='flaticon-left-chevron'></i>", "<i class='flaticon-right-chevron'></i>"],
                responsive: { 0: { items: 1 }, 576: { items: 2 }, 768: { items: 2 }, 1200: { items: 3 } },
            }),
            e(".partner-slides").owlCarousel({
                loop: !0,
                nav: !1,
                dots: !1,
                autoplayHoverPause: !0,
                autoplay: !0,
                margin: 30,
                navText: ["<i class='flaticon-left-chevron'></i>", "<i class='flaticon-right-chevron'></i>"],
                responsive: { 0: { items: 3, margin: 10 }, 576: { items: 4 }, 768: { items: 5 }, 1200: { items: 7 } },
            }),
            e(".feedback-slides").owlCarousel({ loop: 0, nav: !0, dots: !0, autoplayHoverPause: !0, autoplay: 0, autoHeight: !0, items: 1, navText: ["<i class='flaticon-left-chevron'></i>", "<i class='flaticon-right-chevron'></i>"] }),
            e(".team-slides").owlCarousel({
                loop: !0,
                nav: !0,
                dots: !0,
                autoplayHoverPause: !0,
                autoplay: !0,
                center: !0,
                margin: 30,
                navText: ["<i class='flaticon-left-chevron'></i>", "<i class='flaticon-right-chevron'></i>"],
                responsive: { 0: { items: 1 }, 576: { items: 2 }, 768: { items: 2 }, 1200: { items: 3 } },
            }),
            e(".place-image-slides").owlCarousel({
                loop: !0,
                nav: !0,
                dots: !0,
                autoplayHoverPause: !0,
                autoplay: !0,
                items: 1,
                animateOut: "fadeOut",
                navText: ["<i class='flaticon-left-chevron'></i>", "<i class='flaticon-right-chevron'></i>"],
            }),
            (function (e) {
                e(".tab ul.tabs").addClass("active").find("> li:eq(0)").addClass("current"),
                    e(".tab ul.tabs li a").on("click", function (t) {
                        var a = e(this).closest(".tab"),
                            s = e(this).closest("li").index();
                        a.find("ul.tabs > li").removeClass("current"),
                            e(this).closest("li").addClass("current"),
                            a
                                .find(".tab_content")
                                .find("div.tabs_item")
                                .not("div.tabs_item:eq(" + s + ")")
                                .slideUp(),
                            a
                                .find(".tab_content")
                                .find("div.tabs_item:eq(" + s + ")")
                                .slideDown(),
                            t.preventDefault();
                    });
            })(jQuery),
            e(".newsletter-form")
                .validator()
                .on("submit", function (e) {
                    e.isDefaultPrevented() ? (t(), a(!1, "Please enter your email correctly.")) : e.preventDefault();
                }),
            e(".newsletter-form").ajaxChimp({
                url: "https://envytheme.us20.list-manage.com/subscribe/post?u=60e1ffe2e8a68ce1204cd39a5&amp;id=42d6d188d9",
                callback: function (s) {
                    "success" === s.result
                        ? (e(".newsletter-form")[0].reset(),
                          a(!0, "Thank you for subscribing!"),
                          setTimeout(function () {
                              e("#validator-newsletter").addClass("hide");
                          }, 4e3))
                        : t();
                },
            }),
            e(function () {
                e(".accordion")
                    .find(".accordion-title")
                    .on("click", function () {
                        e(this).toggleClass("active"), e(this).next().slideToggle("fast"), e(".accordion-content").not(e(this).next()).slideUp("fast"), e(".accordion-title").not(e(this)).removeClass("active");
                    });
            }),
            e('a[data-imagelightbox="popup-btn"]').imageLightbox({ activity: !0, overlay: !0, button: !0, arrows: !0 }),
            e('a[data-imagelightbox="video"]').imageLightbox({ activity: !0, overlay: !0, button: !0 }),
            e(function () {
                e(".shorting").mixItUp();
            }),
            e(function () {
                e(window).on("scroll", function () {
                    var t = e(window).scrollTop();
                    t > 600 && e(".go-top").addClass("active"), t < 600 && e(".go-top").removeClass("active");
                }),
                    e(".go-top").on("click", function () {
                        e("html, body").animate({ scrollTop: "0" }, 500);
                    });
            });
    }),
        e(window).on("load", function () {
            e(".wow").length && new WOW({ boxClass: "wow", animateClass: "animated", offset: 20, mobile: !0, live: !0 }).init();
        }),
        e(window).on("load", function () {
            e(".preloader").fadeOut();
        });
})(jQuery);
