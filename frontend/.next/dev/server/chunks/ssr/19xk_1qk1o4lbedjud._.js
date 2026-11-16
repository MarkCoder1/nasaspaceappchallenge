module.exports = [
"[project]/frontend/node_modules/leaflet/dist/leaflet-src.js [app-ssr] (ecmascript, async loader)", ((__turbopack_context__) => {

__turbopack_context__.v((parentImport) => {
    return Promise.all([
  "server/chunks/ssr/19xk_leaflet_dist_leaflet-src_16rx7pvsc88sg.js"
].map((chunk) => __turbopack_context__.l(chunk))).then(() => {
        return parentImport("[project]/frontend/node_modules/leaflet/dist/leaflet-src.js [app-ssr] (ecmascript)");
    });
});
}),
"[project]/frontend/node_modules/three/examples/jsm/controls/OrbitControls.js [app-ssr] (ecmascript, async loader)", ((__turbopack_context__) => {

__turbopack_context__.v((parentImport) => {
    return Promise.all([
  "server/chunks/ssr/19xk_three_examples_jsm_controls_OrbitControls_09r9ccj_jvif3.js"
].map((chunk) => __turbopack_context__.l(chunk))).then(() => {
        return parentImport("[project]/frontend/node_modules/three/examples/jsm/controls/OrbitControls.js [app-ssr] (ecmascript)");
    });
});
}),
];