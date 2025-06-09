import { Routes } from '@angular/router';
import { LandingComponent } from './landing/landing.component';
import { SubmissionsComponent } from './submissions/submissions.component';
import { InputComponent } from './input/input.component';
import { authGuard } from './_guards/auth.guard';
import { redirectIfAuthenticatedGuard } from './_guards/redirect-if-auth.guard';

export const routes: Routes = [
    {
        path: '',
        component: LandingComponent,
        canActivate: [redirectIfAuthenticatedGuard]
    },
    {
        path: 'submissions',
        component: SubmissionsComponent,
        canActivate: [authGuard]
    },
    {
        path: 'input',
        component: InputComponent,
        canActivate: [authGuard]
    }
];
