import { HttpInterceptorFn } from "@angular/common/http";
import { environment } from "../../environments/environment.development";

const apiUrl = environment.apiUrl;

export const ApiBaseUrlInterceptor: HttpInterceptorFn = (req, next) => { 
    
    const apiReq = req.clone({ url: `${apiUrl}${req.url}` });
    return next(apiReq);

};