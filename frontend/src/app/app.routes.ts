import { Routes } from '@angular/router';
import { LandingComponent } from './landing/landing.component';
import { SubmissionsComponent } from './submissions/submissions.component';
import { InputComponent } from './input/input.component';

export const routes: Routes = [
    {
        path: '',
        component: LandingComponent
    },
    {
        path: 'submissions',
        component: SubmissionsComponent
    },
    {
        path: 'input',
        component: InputComponent
    }
];
