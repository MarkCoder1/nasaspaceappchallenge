module.exports = [
"[project]/frontend/node_modules/next/dist/build/webpack/loaders/next-flight-loader/track-dynamic-import.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "trackDynamicImport", {
    enumerable: true,
    get: function() {
        return _trackdynamicimport.trackDynamicImport;
    }
});
const _trackdynamicimport = __turbopack_context__.r("[project]/frontend/node_modules/next/dist/server/app-render/module-loading/track-dynamic-import.js [app-ssr] (ecmascript)");
}),
"[project]/frontend/node_modules/next/dist/server/app-render/module-loading/track-dynamic-import.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "trackDynamicImport", {
    enumerable: true,
    get: function() {
        return trackDynamicImport;
    }
});
const _invarianterror = __turbopack_context__.r("[project]/frontend/node_modules/next/dist/shared/lib/invariant-error.js [app-ssr] (ecmascript)");
const _isthenable = __turbopack_context__.r("[project]/frontend/node_modules/next/dist/shared/lib/is-thenable.js [app-ssr] (ecmascript)");
const _trackmoduleloadingexternal = __turbopack_context__.r("[externals]/next/dist/server/app-render/module-loading/track-module-loading.external.js [external] (next/dist/server/app-render/module-loading/track-module-loading.external.js, cjs)");
function trackDynamicImport(modulePromise) {
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    if (!(0, _isthenable.isThenable)(modulePromise)) {
        // We're expecting `import()` to always return a promise. If it's not, something's very wrong.
        throw new _invarianterror.InvariantError('`trackDynamicImport` should always receive a promise. Something went wrong in the dynamic imports transform.');
    }
    // Even if we're inside a prerender and have `workUnitStore.cacheSignal`, we always track the promise globally.
    // (i.e. via the global `moduleLoadingSignal` that `trackPendingImport` uses internally).
    //
    // We do this because the `import()` promise might be cached in userspace:
    // (which is quite common for e.g. lazy initialization in libraries)
    //
    //   let promise;
    //   function doDynamicImportOnce() {
    //     if (!promise) {
    //       promise = import("...");
    //       // transformed into:
    //       // promise = trackDynamicImport(import("..."));
    //     }
    //     return promise;
    //   }
    //
    // If multiple prerenders (e.g. multiple pages) depend on `doDynamicImportOnce`,
    // we have to wait for the import *in all of them*.
    // If we only tracked it using `workUnitStore.cacheSignal.trackRead()`,
    // then only the first prerender to call `doDynamicImportOnce` would wait --
    // Subsequent prerenders would re-use the existing `promise`,
    // and `trackDynamicImport` wouldn't be called again in their scope,
    // so their respective CacheSignals wouldn't wait for the promise.
    (0, _trackmoduleloadingexternal.trackPendingImport)(modulePromise);
    return modulePromise;
}
}),
"[project]/frontend/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/frontend/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)").vendored['react-ssr'].ReactJsxDevRuntime;
}),
"[project]/frontend/node_modules/next/dist/shared/lib/invariant-error.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "InvariantError", {
    enumerable: true,
    get: function() {
        return InvariantError;
    }
});
class InvariantError extends Error {
    constructor(message, options){
        super(`Invariant: ${message.endsWith('.') ? message : message + '.'} This is a bug in Next.js.`, options);
        this.name = 'InvariantError';
    }
}
}),
"[project]/frontend/node_modules/next/dist/shared/lib/is-thenable.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

/**
 * Check to see if a value is Thenable.
 *
 * @param promise the maybe-thenable value
 * @returns true if the value is thenable
 */ Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "isThenable", {
    enumerable: true,
    get: function() {
        return isThenable;
    }
});
function isThenable(promise) {
    return promise !== null && typeof promise === 'object' && 'then' in promise && typeof promise.then === 'function';
}
}),
];

//# sourceMappingURL=19xk_next_dist_0d2kzd72uq_16._.js.map