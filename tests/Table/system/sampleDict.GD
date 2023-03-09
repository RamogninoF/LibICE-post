/*---------------------------------------------------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  1.3                                   |
|   \\  /    A nd           | Web:      http://www.openfoam.org               |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/

FoamFile
{
    version         2.0;
    format          ascii;

    root            "";
    case            "";
    instance        "";
    local           "";

    class           dictionary;
    object          sampleDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //


interpolationScheme cellPointFace;
//interpolationScheme cellPoint;
//interpolationScheme cell;

setFormat     raw;
//setFormat     xmgr;
//setFormat     gnuplot;

surfaceFormat raw;


sets      
(
    sample15mm
    {
        type        uniform;
	    axis            x;
        start           (-54e-3   0.00 18.9e-3);
        end           (54e-3   0.00 18.9e-3);
        nPoints         300;
    }

    sample25mm
    {
        type        uniform;
	    axis            x;
        start           (-54e-3   0.00 28.9e-3);
        end           (54e-3   0.00 28.9e-3);
        nPoints         300;
    }
    
    sample45mm
    {
        type        uniform;
	    axis            x;
        start           (-54e-3   0.00 8.9e-3);
        end           (54e-3   0.00 8.9e-3);
        nPoints         150;
    }
    sampleAxial
    {
        type        uniform;
	    axis            distance;
        start           (2.2e-4   2.2e-4 53.9e-3);
        end             (2.2e-4   2.2e-4 -54e-3);
        nPoints         200;
    }
);

fields          
(
Z
Z2
Ux
Uy
Uz
);

surfaces
(
);


// ************************************************************************* //
