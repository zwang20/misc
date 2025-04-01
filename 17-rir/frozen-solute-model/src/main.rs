/*#[derive(Debug, serde::Serialize, serde::Deserialize)]
enum FunctionalType {
    M062X,
}

#[allow(non_camel_case_types)]
#[derive(Debug, serde::Serialize, serde::Deserialize)]
enum BasisType {
    _6_31pG_D,
    def2SVP,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct QuantumMechanicsType {
    functional_type: FunctionalType,
    basis_type: BasisType,
}
*/

// manual backfilling:
// SELECT MIN(local_path + 1) FROM runs WHERE (local_path + 1) NOT IN (SELECT local_path FROM runs);
// SELECT * FROM molecules WHERE compound_id NOT IN (SELECT compound_id FROM runs) ORDER BY rotatable_bonds ASC, num_atoms ASC LIMIT 5;

// INSERT INTO runs VALUES ('mobley_6714389', 'RelaxedMinEquilGAFF', 'Received', 12, 'gadi', '/scratch/cw7/mw7780/.automated/12/');
// INSERT INTO runs VALUES ('mobley_303222', 'RelaxedMinEquilGAFF', 'Received', 13, 'gadi', '/scratch/cw7/mw7780/.automated/13/');
// python prep.py mobley_303222 13 gadi
// rsync -r data/13/ gadi:/scratch/cw7/mw7780/.automated/13/
// UPDATE runs SET status = 'Running' WHERE local_path = 13;

// INSERT INTO runs VALUES ('mobley_3867265', 'RelaxedMinEquilGAFF', 'Received', 14, 'gadi', '/scratch/cw7/mw7780/.automated/14/');
// python prep.py mobley_3867265 14 gadi
// rsync -r data/14/ gadi:/scratch/cw7/mw7780/.automated/14/
// UPDATE runs SET status = 'Running' WHERE local_path = 14;

// INSERT INTO runs VALUES ('mobley_9121449', 'RelaxedMinEquilGAFF', 'Received', 15, 'gadi', '/scratch/cw7/mw7780/.automated/15/');
// python prep.py mobley_9121449 15 gadi
// rsync -r data/15/ gadi:/scratch/cw7/mw7780/.automated/15/
// UPDATE runs SET status = 'Running' WHERE local_path = 15;

// INSERT INTO runs VALUES ('mobley_3982371', 'RelaxedMinEquilGAFF', 'Received', 16, 'gadi', '/scratch/cw7/mw7780/.automated/16/');
// python prep.py mobley_3982371 16 gadi
// rsync -r data/16/ gadi:/scratch/cw7/mw7780/.automated/16/
// UPDATE runs SET status = 'Running' WHERE local_path = 16;

// INSERT INTO runs VALUES ('mobley_1075836', 'RelaxedMinEquilGAFF', 'Received', 21, 'gadi', '/scratch/cw7/mw7780/.automated/21/');
// python prep.py mobley_1075836 21 gadi
// rsync -r data/21/ gadi:/scratch/cw7/mw7780/.automated/21/
// UPDATE runs SET status = 'Running' WHERE local_path = 21;

// INSERT INTO runs VALUES ('mobley_4193752', 'RelaxedMinEquilGAFF', 'Received', 33, 'gadi', '/scratch/cw7/mw7780/.automated/33/');
// python prep.py mobley_4193752 33 gadi
// rsync -r data/33/ gadi:/scratch/cw7/mw7780/.automated/33/
// UPDATE runs SET status = 'Running' WHERE local_path = 33;

// INSERT INTO runs VALUES ('mobley_1903702', 'RelaxedMinEquilGAFF', 'Received', 310, 'gadi', '/scratch/cw7/mw7780/.automated/310/');
// python prep.py mobley_1903702 310 gadi
// rsync -r data/310/ gadi:/scratch/cw7/mw7780/.automated/310/
// UPDATE runs SET status = 'Running' WHERE local_path = 310;

// INSERT INTO runs VALUES ('mobley_5816127', 'RelaxedMinEquilGAFF', 'Received', 302, 'gadi', '/scratch/cw7/mw7780/.automated/302/');
// python prep.py mobley_5816127 302 gadi
// rsync -r data/302/ gadi:/scratch/cw7/mw7780/.automated/302/
// UPDATE runs SET status = 'Running' WHERE local_path = 302;

// INSERT INTO runs VALUES ('mobley_1929982', 'CREST', 'Running', 303, 'katana', '/srv/scratch/z5358697/.automated/303');
// python prep.py mobley_5816127 302 gadi
// rsync -r data/302/ gadi:/scratch/cw7/mw7780/.automated/302/
// UPDATE runs SET status = 'Running' WHERE local_path = 302;

// Deleting entries
// DELETE FROM runs WHERE local_path=-1;

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct Molecule {
    compound_id: String,
    smiles: String,
    iupac: String,
    experimental_value: f64,
    experimental_uncertainty: f64,
    calculated_value: f64,
    calculated_uncertainty: f64,
    experimental_reference: String,
    calculated_reference: String,
    notes: Option<String>,
    rotatable_bonds: u16,
    num_atoms: u16,
}

#[derive(Debug, PartialEq, serde::Serialize, serde::Deserialize)]
enum StatusType {
    Planned,
    Running,
    Received,
    Finished,
}

#[allow(non_camel_case_types)]
#[derive(Debug, PartialEq, serde::Serialize, serde::Deserialize)]
enum RemoteHostType {
    localhost,
    katana,
    gadi,
    setonix,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
enum RunType {
    RelaxedMinEquilGAFF,
    RelaxedForwardGAFF,
    RelaxedReversedGAFF,
    CREST,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct Run {
    compound_id: String,
    run_type: RunType,
    status: StatusType,
    local_path: u16,
    remote_host: RemoteHostType,
    remote_path: String,
}

#[allow(non_snake_case)]
#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct KatanaJob {
    Job_Name: u16,
    job_state: char,
}

#[allow(non_snake_case)]
#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct GadiJob {
    Job_Name: String,
    job_state: char,
}

#[derive(Debug, PartialEq, serde::Serialize, serde::Deserialize)]
enum SetonixJobState {
    PENDING,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct SetonixJob {
    name: String,
    job_state: SetonixJobState,
}

fn update_run_status(
    local_path: u16,
    new_status: StatusType,
    connection: &rusqlite::Connection,
) -> Result<(u16, StatusType), Box<dyn std::error::Error>> {
    connection.execute(
        &format!(
            "UPDATE runs SET status = '{:?}' WHERE local_path = {}",
            new_status, local_path
        ),
        [],
    )?;
    Ok((local_path, new_status))
}

fn receive_files(
    Run {
        compound_id: _,
        run_type: _,
        status,
        local_path,
        remote_host,
        remote_path,
    }: Run,
    connection: &rusqlite::Connection,
) {
    // check if status is correct
    if status != StatusType::Running {
        return;
    }
    match std::process::Command::new("rsync")
        .arg("-r")
        .arg(format!("{:?}:{}", remote_host, remote_path))
        .arg(format!("data/{}", local_path))
        .output()
    {
        Ok(_) => println!(
            "{:?}",
            update_run_status(local_path, StatusType::Received, connection)
        ),
        Err(e) => println!("{:?}", e),
    }
}

fn submit_job(
    Run {
        compound_id: _,
        run_type: _,
        status,
        local_path,
        remote_host,
        remote_path,
    }: &Run,
) -> Result<(), Box<dyn std::error::Error>> {
    println!(
        "submit job {}, {:?}, {}",
        local_path, remote_host, remote_path
    );

    if status != &StatusType::Planned {
        println!("invalid status {:?}", status);
        Err("Invalid status")?
    }

    match remote_host {
        RemoteHostType::localhost => Err("invalid target localhost")?,
        RemoteHostType::setonix => run_program(vec![
            "ssh",
            &format!("{:?}", remote_host),
            &format!("cd {}; sbatch {}", remote_path, local_path),
        ]),
        RemoteHostType::katana | RemoteHostType::gadi => run_program(vec![
            "ssh",
            &format!("{:?}", remote_host),
            &format!("cd {}; qsub {}", remote_path, local_path),
        ]),
    }?;

    Ok(())
}

fn copy(source: &str, dest: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("copying from {} to {}", source, dest);
    std::fs::copy(source, dest)?;
    Ok(())
}

fn create_dir_if(dir: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("creating directory if not exists {}", dir);
    if !std::path::Path::new(&dir).exists() {
        std::fs::create_dir(dir)?;
    }
    Ok(())
}

fn run_program(args: Vec<&str>) -> Result<(), Box<dyn std::error::Error>> {
    println!("running program with args {:?}", args);
    let mut args = args.into_iter();
    let mut process = std::process::Command::new(args.next().ok_or("No command found")?);
    for arg in args {
        process.arg(arg);
    }
    let output = process.output()?;
    println!("{:#?}", output);
    if output.status.success() {
        Ok(())
    } else {
        Err("program exit unsuccessful")?
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Loading database");
    let connection = rusqlite::Connection::open("frozen_solute_model.db")?;
    let mut statement = connection.prepare("SELECT * FROM molecules")?;
    let molecules = serde_rusqlite::from_rows::<Molecule>(statement.query([])?);
    for molecule in molecules {
        molecule?;
    }

    let mut statement = connection.prepare("SELECT * FROM runs")?;
    let runs = serde_rusqlite::from_rows::<Run>(statement.query([])?);
    for run in runs {
        run?;
    }

    let modified = std::fs::metadata("server/gadi.json")?
        .modified()?
        .duration_since(std::time::SystemTime::UNIX_EPOCH)?
        + std::time::Duration::from_secs(30);
    let now = std::time::SystemTime::now().duration_since(std::time::SystemTime::UNIX_EPOCH)?;

    if modified < now {
        println!("File Older than 30 Seconds, Not sleeping")
    } else {
        let sleep = modified - now;
        println!("Sleeping for {:?}", sleep);
        std::thread::sleep(sleep);
    }

    println!("Getting run data");
    let mut jobs: Vec<u16> = vec![];

    // katana
    {
        println!("Updating Katana");
        let katana_raw_json = std::fs::File::create("server/katana_raw.json")?;
        let output = std::process::Command::new("ssh")
            .arg("katana")
            .arg("qstat -f -F json")
            .stdout(katana_raw_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());
        let katana_json = std::fs::File::create("server/katana.json")?;
        let output = std::process::Command::new("jq")
            .arg("[.Jobs | to_entries[] | select((.value.Job_Owner | startswith(\"z5358697\")) or (.value.Job_Owner | startswith(\"z5382435\"))) | .value]")
            .arg("server/katana_raw.json")
            .stdout(katana_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());
        let output = std::process::Command::new("rm")
            .arg("server/katana_raw.json")
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());

        jobs.append(
            &mut serde_json::from_str::<Vec<KatanaJob>>(&std::fs::read_to_string(
                "server/katana.json",
            )?)
            .unwrap_or_default()
            .into_iter()
            .map(|i| i.Job_Name)
            .collect::<Vec<u16>>(),
        );
    }

    // gadi
    {
        println!("Updating gadi");
        let gadi_raw_json = std::fs::File::create("server/gadi_raw.json")?;
        let output = std::process::Command::new("ssh")
            .arg("gadi")
            .arg("qstat -f -F json")
            .stdout(gadi_raw_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());
        let gadi_json = std::fs::File::create("server/gadi.json")?;
        let output = std::process::Command::new("jq")
            .arg("try([.Jobs | to_entries[] | select(.value.Job_Owner | startswith(\"mw7780\")) | .value]) // []")
            .arg("server/gadi_raw.json")
            .stdout(gadi_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());

        jobs.append(
            &mut serde_json::from_str::<Vec<GadiJob>>(&std::fs::read_to_string(
                "server/gadi.json",
            )?)
            .unwrap_or_default()
            .into_iter()
            .map(|i| i.Job_Name.parse::<u16>().unwrap())
            .collect::<Vec<u16>>(),
        );
    }

    // setonix
    {
        println!("Updating setonix");
        let setonix_raw_json = std::fs::File::create("server/setonix_raw.json")?;
        let output = std::process::Command::new("ssh")
            .arg("setonix")
            .arg("squeue --user mwang1 --json")
            .stdout(setonix_raw_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());
        let setonix = std::fs::File::create("server/setonix.json")?;
        let output = std::process::Command::new("jq")
            .arg("[.jobs[] | {name: .name, job_state: .job_state[0]}]")
            .arg("server/setonix_raw.json")
            .stdout(setonix)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());

        jobs.append(
            &mut serde_json::from_str::<Vec<SetonixJob>>(&std::fs::read_to_string(
                "server/setonix.json",
            )?)
            .unwrap_or_default()
            .into_iter()
            .map(|i| i.name.parse::<u16>().unwrap())
            .collect::<Vec<u16>>(),
        );
    }

    jobs.sort_unstable(); // they are supposed to be unique anyway
    println!("Jobs: {:?}", jobs);
    // assert!(jobs.len() < 10);

    let mut katana_queue_length: u8 =
        serde_json::from_str::<Vec<KatanaJob>>(&std::fs::read_to_string("server/katana.json")?)
            .unwrap_or_default()
            .into_iter()
            .fold(0, |acc, x| acc + (x.job_state == 'Q') as u8);
    let mut gadi_queue_length: u8 =
        serde_json::from_str::<Vec<GadiJob>>(&std::fs::read_to_string("server/gadi.json")?)
            .unwrap_or_default()
            .into_iter()
            .fold(0, |acc, x| acc + (x.job_state == 'Q') as u8);
    let mut setonix_queue_length: u8 =
        serde_json::from_str::<Vec<SetonixJob>>(&std::fs::read_to_string("server/setonix.json")?)
            .unwrap_or_default()
            .into_iter()
            .fold(0, |acc, x| {
                acc + (x.job_state == SetonixJobState::PENDING) as u8
            });

    gadi_queue_length += 0;
    println!("gadi queue length: {}", gadi_queue_length);
    println!("setonix queue length: {}", setonix_queue_length);

    let mut planned: u8 = 0;
    let mut statement = connection.prepare("SELECT * FROM runs")?;
    let runs = serde_rusqlite::from_rows::<Run>(statement.query([])?);
    for run in runs {
        let run = run?;
        match &run.status {
            StatusType::Planned => 'match_status: {
                planned += 1;

                if run.remote_host == RemoteHostType::localhost {
                    if katana_queue_length < 3 {
                        let output = connection.execute(
                            // TODO: do something other than katana
                            &format!(
                                "UPDATE runs SET remote_path = '/srv/scratch/z5358697/.automated/{}/', remote_host = 'katana' WHERE local_path = {}",
                                run.local_path, run.local_path
                            ),
                            [],
                        );
                        println!("pick remote host {:?}", output);
                        katana_queue_length += 1;
                    }
                    /*else if setonix_queue_length < 0 {
                        connection.execute(
                            &format!(
                                "UPDATE runs SET remote_path = '/scratch/pawsey0265/mwang1/.automated/{}/', remote_host = 'setonix' WHERE local_path = {}",
                                run.local_path, run.local_path
                            ),
                            [],
                        )?;
                        setonix_queue_length += 1;
                    } */
                    else {
                        println!("all queues busy, skipping");
                    }
                    break 'match_status;
                }

                match &run.run_type {
                    RunType::RelaxedMinEquilGAFF => {
                        let output = std::process::Command::new("python")
                            .arg("prep.py")
                            .arg(&run.compound_id)
                            .arg(run.local_path.to_string())
                            .output()?;
                        println!("python prep.py {:?}", output);
                        if !output.status.success() {
                            break 'match_status;
                        }

                        let output = std::process::Command::new("rsync")
                            .arg("-r")
                            .arg(format!("data/{}/", run.local_path))
                            .arg(format!("{:?}:{}", run.remote_host, run.remote_path))
                            .output()?;
                        println!("rsync copy to server {:?}", output);
                        if !output.status.success() {
                            break 'match_status;
                        }

                        let output = std::process::Command::new("ssh")
                            .arg(format!("{:?}", run.remote_host))
                            .arg(format!("cd {}; qsub {}", run.remote_path, run.local_path))
                            .output()?;
                        println!("ssh start remote job {:?}", output);
                        if !output.status.success() {
                            break 'match_status;
                        }

                        println!(
                            "{:?}",
                            update_run_status(run.local_path, StatusType::Running, &connection)
                        );
                        katana_queue_length += 1;
                    }
                    RunType::RelaxedForwardGAFF | RunType::RelaxedReversedGAFF => {
                        let mut statement = connection.prepare(&format!(
                            "SELECT * FROM runs WHERE compound_id == '{}' AND run_type = 'RelaxedMinEquilGAFF'",
                            run.compound_id,
                        ))?;
                        let min_equil_path = serde_rusqlite::from_rows::<Run>(statement.query([])?)
                            .next()
                            .ok_or("No prep found")??
                            .local_path;

                        create_dir_if(&format!("data/{}", run.local_path))?;

                        for suffix in [".prmtop", ".pdb", "_equil.coor", "_equil.vel", "_equil.xsc"]
                        {
                            let source =
                                format!("data/{}/{}{}", min_equil_path, run.compound_id, suffix);
                            let dest =
                                format!("data/{}/{}{}", run.local_path, run.compound_id, suffix);
                            copy(&source, &dest)?;
                        }

                        copy("fep.tcl", &format!("data/{}/fep.tcl", run.local_path))?;

                        // run prod script
                        match &run.run_type {
                            RunType::RelaxedForwardGAFF => run_program(vec![
                                "python",
                                "prod.forward.py",
                                &run.compound_id,
                                &run.local_path.to_string(),
                            ])?,
                            RunType::RelaxedReversedGAFF => run_program(vec![
                                "python",
                                "prod.reversed.py",
                                &run.compound_id,
                                &run.local_path.to_string(),
                            ])?,
                            _ => panic!(),
                        }

                        // copy to server
                        run_program(vec![
                            "rsync",
                            "-r",
                            &format!("data/{}/", run.local_path),
                            &format!("{:?}:{}", run.remote_host, run.remote_path),
                        ])?;

                        // start remote job
                        submit_job(&run)?;

                        println!(
                            "{:?}",
                            update_run_status(run.local_path, StatusType::Running, &connection)
                        );

                        match run.remote_host {
                            RemoteHostType::localhost => {}
                            RemoteHostType::katana => katana_queue_length += 1,
                            RemoteHostType::gadi => gadi_queue_length += 1,
                            RemoteHostType::setonix => setonix_queue_length += 1,
                        }
                    }
                    RunType::CREST => {
                        // TODO: do something

                        create_dir_if(&format!("data/{}", run.local_path))?;

                        run_program(vec![
                            "python",
                            "mol2-to-xyz.py",
                            &format!("FreeSolv/mol2files_gaff/{}.mol2", run.compound_id),
                            &format!("data/{}/{}.xyz", run.local_path, run.compound_id),
                        ])?;

                        run_program(vec![
                            "python",
                            "crest.py",
                            &format!("data/{}/{}", run.local_path, run.local_path),
                            &run.compound_id,
                        ])?;

                        run_program(vec![
                            "rsync",
                            "-r",
                            &format!("data/{}/", run.local_path),
                            &format!("{:?}:{}", run.remote_host, run.remote_path),
                        ])?;

                        // start remote job
                        submit_job(&run)?;

                        println!(
                            "{:?}",
                            update_run_status(run.local_path, StatusType::Running, &connection)
                        );

                        match run.remote_host {
                            RemoteHostType::localhost => {}
                            RemoteHostType::katana => katana_queue_length += 1,
                            RemoteHostType::gadi => gadi_queue_length += 1,
                            RemoteHostType::setonix => setonix_queue_length += 1,
                        }
                    }
                }
            }
            StatusType::Running => {
                if !jobs.iter().any(|name| name == &run.local_path) {
                    receive_files(run, &connection);
                }
            }
            StatusType::Received => match &run.run_type {
                RunType::RelaxedMinEquilGAFF => {}
                _ => {}
            },
            StatusType::Finished => {}
        }
    }

    if planned >= 3 {
        return Ok(());
    }
    println!("Generating Jobs");

    let mut statement = connection.prepare(
        "\
            SELECT * FROM molecules \
            WHERE compound_id NOT IN (SELECT compound_id FROM runs WHERE run_type == 'CREST') \
            ORDER BY rotatable_bonds ASC, num_atoms ASC LIMIT 1\
        ",
    )?;

    match serde_rusqlite::from_rows::<Molecule>(statement.query([])?)
        .next()
        .ok_or(())
    {
        Ok(molecule) => {
            let query = format!(
                "INSERT INTO runs (compound_id, run_type, status, remote_host, remote_path) VALUES ('{}', '{:?}', '{:?}', '{:?}', '{}')",
                molecule?.compound_id,
                RunType::CREST,
                StatusType::Planned,
                RemoteHostType::localhost,
                "/dev/null/"
            );
            println!("{}", query);
            connection.execute(&query, [])?;
        }
        Err(_) => {}
    }

    if planned >= 2 {
        return Ok(());
    }

    let mut statement = connection.prepare("\
        SELECT * FROM molecules \
        WHERE compound_id NOT IN (SELECT compound_id FROM runs WHERE run_type == 'RelaxedReversedGAFF') \
        AND compound_id IN (SELECT compound_id FROM runs WHERE run_type == 'RelaxedForwardGAFF') \
        AND compound_id IN (SELECT compound_id FROM runs WHERE run_type == 'RelaxedMinEquilGAFF' AND status == 'Received') \
        ORDER BY rotatable_bonds ASC, num_atoms ASC LIMIT 1\
    ")?;

    match serde_rusqlite::from_rows::<Molecule>(statement.query([])?)
        .next()
        .ok_or(())
    {
        Ok(molecule) => {
            let query = format!(
                "INSERT INTO runs (compound_id, run_type, status, remote_host, remote_path) VALUES ('{}', '{:?}', '{:?}', '{:?}', '{}')",
                molecule?.compound_id,
                RunType::RelaxedReversedGAFF,
                StatusType::Planned,
                RemoteHostType::localhost,
                "/dev/null/"
            );
            println!("{}", query);
            connection.execute(&query, [])?;
        }
        Err(_) => {}
    }

    if planned >= 1 {
        return Ok(());
    }

    let mut statement = connection.prepare("\
        SELECT * FROM molecules \
        WHERE compound_id NOT IN (SELECT compound_id FROM runs WHERE run_type == 'RelaxedForwardGAFF') \
        AND compound_id IN (SELECT compound_id FROM runs WHERE run_type == 'RelaxedMinEquilGAFF' AND status == 'Received') \
        ORDER BY rotatable_bonds ASC, num_atoms ASC LIMIT 5\
    ")?;
    let molecule = serde_rusqlite::from_rows::<Molecule>(statement.query([])?)
        .next()
        .ok_or("All done!")??;
    println!("{:?}", molecule);
    connection
            .execute(&format!("INSERT INTO runs (compound_id, run_type, status, remote_host, remote_path) VALUES ('{}', '{:?}', '{:?}', '{:?}', '{}')", molecule.compound_id, RunType::RelaxedForwardGAFF, StatusType::Planned, RemoteHostType::localhost, "/dev/null/"), [])?;
    Ok(())
}
